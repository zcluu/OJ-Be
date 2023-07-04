import contextlib

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from OJ.app.settings import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=True)
Base = declarative_base()


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

# @contextlib.contextmanager
# def get_session():
#     session = SessionLocal()  # 创建会话
#     try:
#         yield session
#         session.commit()
#     except Exception:
#         session.rollback()
#         raise
#     finally:
#         session.close()
