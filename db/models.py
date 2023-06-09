import time

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

from .database import Base


class UserInfo(Base):
    __tablename__ = 'UserInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(200))
    password = Column(String(200))
    is_supper = Column(Boolean, default=False)
    lastlogin = Column(DateTime, default=datetime.datetime.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSession(Base):
    __tablename__ = 'UserSession'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    token = Column(String(200))
    sess2user = relationship('UserInfo', backref='user2sess')
    time = Column(DateTime,
                  onupdate=datetime.datetime.now(),
                  default=datetime.datetime.now()
                  )
    expire_time = Column(DateTime,
                         onupdate=datetime.datetime.now() + datetime.timedelta(days=1),
                         default=datetime.datetime.now() + datetime.timedelta(days=1)
                         )

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class RestaurantInfo(Base):
    __tablename__ = 'RestaurantInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200))
    admin = Column(Integer, ForeignKey('UserInfo.id'))
    r2u = relationship('UserInfo', backref='u2r')
    is_available = Column(Boolean, default=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TableInfo(Base):
    __tablename__ = 'TableInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant = Column(Integer, ForeignKey('RestaurantInfo.id'))
    category = Column(Integer)
    total_num = Column(Integer)
    used_num = Column(Integer)
    waiting_num = Column(Integer)
    t2r = relationship('RestaurantInfo', backref='r2t')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WaitingList(Base):
    __tablename__ = 'WaitingList'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table = Column(Integer, ForeignKey('TableInfo.id'))
    user = Column(Integer, ForeignKey('UserInfo.id'))
    nickname = Column(String(20))
    phonenum = Column(String(15))
    create_time = Column(DateTime, default=datetime.datetime.now)
    status = Column(Integer)
    w2t = relationship('TableInfo', backref='t2w')
    w2u = relationship('UserInfo', backref='u2w')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
