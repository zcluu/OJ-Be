from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from OJ.app.settings import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class BaseModel(object):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
