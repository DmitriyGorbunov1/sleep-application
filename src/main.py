from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import *


# format: postgresql://user:password@host:port/dbname[?key=value&key=value...]
engine = create_engine("postgresql://postgres:root@127.0.0.1:5432/test")

DeclarativeBase.metadata.drop_all(bind=engine)
DeclarativeBase.metadata.create_all(bind=engine, tables=[User.__table__])
DeclarativeBase.metadata.bind = engine

Session = sessionmaker(bind=engine)

db = Database(Session)