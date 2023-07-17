from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import importlib

__all__ = ['Base', 'BaseModel']

Base = declarative_base()
SessionLocal = None
engine = None


def create_connection():
    global engine, SessionLocal
    settings = importlib.import_module('OJ.app.settings')
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=True)


class BaseModel(object):
    def to_dict(self, filter_fields: list = []):
        if not filter_fields:
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        else:
            return {c: getattr(self, c) for c in filter_fields}


def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()
