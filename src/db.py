from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


DeclarativeBase = declarative_base()

class User(DeclarativeBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    hash = Column(String)
    salt = Column(String)
    goal = Column(Integer)
    age_group = Column(Integer)
    wakeup_time = Column(String)
    bedtime = Column(String)
    goodsleep_hours = Column(Integer)
    regime_compliance = Column(Boolean)
    session = relationship("AuthSession", cascade="all, delete-orphan")

    def __repr__(self):
        output = f"table: {self.__tablename__}\n"
        output += f"id: {repr(self.id)}\n"
        output += f"email: {repr(self.email)}\n"
        output += f"name: {repr(self.name)}\n"
        output += f"hash: {repr(self.hash)}\n"
        output += f"salt: {repr(self.salt)}\n"
        output += f"goal: {repr(self.goal)}\n"
        output += f"age_group: {repr(self.age_group)}\n"
        output += f"wakeup_time: {repr(self.wakeup_time)}\n"
        output += f"bedtime: {repr(self.bedtime)}\n"
        output += f"goodsleep_hours: {repr(self.goodsleep_hours)}\n"
        output += f"regime_compliance: {repr(self.regime_compliance)}\n"
        return output

class AuthSession(DeclarativeBase):
    __tablename__ = "auth_session"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    session_id = Column(String)
    create_date = Column(DateTime)
    expire_date = Column(DateTime)

    def __repr__(self):
        output = f"table: {self.__tablename__}\n"
        output += f"id: {repr(self.id)}\n"
        output += f"user_id: {repr(self.user_id)}\n"
        output += f"session_id: {repr(self.session_id)}\n"
        output += f"create_date: {repr(self.create_date)}\n"
        output += f"expire_date: {repr(self.expire_date)}\n"
        return output

class Database:
    def __init__(self, Session):
        self.Session = Session

    def with_session(function):
        def wrapper(self, *args, **kwargs):
            session = None
            result = None

            try:
                session = self.Session()
                result = function(self, session=session, *args, **kwargs)
            except Exception as ex:
                print(ex)
                if session is not None:
                    session.rollback()
            if session is not None:
                session.close()

            return result
        
        return wrapper
    

    @with_session
    def get(self, value, object=User, by=User.email, session=None):
        return session.query(object).filter(by == value).first()

    @with_session
    def add(self, object, session=None):
        session.add(object)
        session.commit()

    @with_session
    def delete(self, value, object=User, by=User.email, session=None):
        obj = session.query(object).filter(by == value).first()
        if obj is not None:
            session.delete(obj)
            session.commit()

    @with_session
    def update(self, value, new_object, by=User.email, session=None):
        obj = session.query(type(new_object)).filter(by == value).first()
        
        if obj is not None:
            # gets public object class' fields
            keys = [elem for elem in vars(type(new_object)).keys() if not elem.startswith("_") and elem != "id"]
            
            for key in keys:
                if hasattr(obj, key):
                    setattr(obj, key, getattr(new_object, key))

            session.commit()

    @with_session
    def append_session(self, value, child, by=User.email, session=None):
        obj = session.query(User).filter(by == value).first()
        
        if obj is not None:
            obj.session.append(child)
            session.commit()