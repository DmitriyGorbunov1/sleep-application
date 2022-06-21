from os import environ
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, HTTPException
from hashlib import md5
from uuid import uuid4
from datetime import datetime

from src.db import DeclarativeBase, Database, Statistics, User, AuthSession
from src.models.auth import LoginModel, UserModel
from src.models.stats import StatisticsModel


# format: postgresql://user:password@host:port/dbname[?key=value&key=value...]
engine = create_engine(f"postgresql://postgres:{environ['DB_PASSWORD']}@127.0.0.1:5432/main")

# DeclarativeBase.metadata.drop_all(bind=engine)
DeclarativeBase.metadata.create_all(bind=engine)
DeclarativeBase.metadata.bind = engine

Session = sessionmaker(bind=engine)

db = Database(Session)
app = FastAPI()


def verify_session(function):
    @wraps(function)
    async def wrapper(session_id: str, user, *args, **kwargs):
        session = db.get(session_id, object=AuthSession, by=AuthSession.session_id)
        if not session:
            raise HTTPException(status_code=403, detail="invalid session")
        
        if datetime.now() >= session.expire_date:
            await db.delete(session_id, object=AuthSession, by=AuthSession.session_id)
            raise HTTPException(status_code=403, detail="invalid session")
        else:
            user = db.get(session.user_id, by=User.id)
            result = await function(session_id=session_id, user=user, *args, **kwargs)
            return result
    
    return wrapper

async def create_session(user: User, is_user_created=True):
    session_id = uuid4()
    create_date = datetime.now()
    expire_date = create_date.replace(year=create_date.year + 1)
    session = AuthSession(session_id=str(session_id), create_date=create_date, expire_date=expire_date)
    db.append_child(user.email, "session", session, obj=[user, None][is_user_created])
    db.add(session)
    return session_id


@app.post("/register")
async def post_register(user: UserModel):
    db_user = db.get(user.email)
    if db_user is not None:
        raise HTTPException(status_code=403, detail="user already registered")

    # User
    values = dict(user)
    values.pop("password")
    db_user = User(**values)
    db_user.salt = uuid4().hex
    db_user.hash = md5((user.password + db_user.salt).encode()).hexdigest()
    # Session
    session_id = await create_session(db_user, is_user_created=False)
    db.add(db_user)

    return str(session_id)

@app.post("/login")
async def post_login(user: LoginModel):
    db_user = db.get(user.email)
    if db_user is None:
        raise HTTPException(status_code=403, detail="can't find user")

    if md5((user.password + db_user.salt).encode()).hexdigest() == db_user.hash:
        return str(await create_session(db_user))
    
    raise HTTPException(status_code=403, detail="wrong password")

@app.post("/send_stats")
@verify_session
async def post_stats(session_id: str, statistics: StatisticsModel, user=None):
    if user is None:
        raise HTTPException(status_code=403, detail="can't find user")
    
    values = dict(statistics)
    stats = Statistics(**values)
    stats.date = str(datetime.now().date())
    db.append_child(user.email, "statistics", stats)
    db.add(stats)