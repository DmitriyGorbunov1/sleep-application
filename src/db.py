from typing import Collection
from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


class RepresentableTable():
    def __repr__(self):
        childs = ["session", "statistics"]
        keys = [elem for elem in vars(type(self)).keys() if not elem.startswith("_") and elem not in childs]
        keys = ["__tablename__"] + keys
        output = [f"{key}: {repr(getattr(self, key))}" for key in keys]
        return "\n".join(output)
        

DeclarativeBase = declarative_base()

class User(DeclarativeBase, RepresentableTable):
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
    statistics = relationship("Statistics", cascade="all, delete-orphan")

class Statistics(DeclarativeBase, RepresentableTable):
    __tablename__ = "statistics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    date = Column(String)
    sleep_hours = Column(String)
    wakeup_time = Column(String)
    bedtime = Column(String)
    fastsleep_time = Column(String)
    slowsleep_time = Column(String)
    gotobed_time = Column(String)
    sleep_quality = Column(Integer)

class AuthSession(DeclarativeBase, RepresentableTable):
    __tablename__ = "auth_session"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    session_id = Column(String)
    create_date = Column(DateTime)
    expire_date = Column(DateTime)


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
    def append_child(self, value, childfield, child, obj=None, object=User, by=User.email, session=None):
        if obj is None:
            obj = session.query(object).filter(by == value).first()
        
        if obj is not None:
            getattr(obj, childfield).append(child)
            session.commit()