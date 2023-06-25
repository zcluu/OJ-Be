from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime

from OJ.db.database import Base, BaseModel
from OJ.util.common import hash256
from OJ.util.constant import *


class SysAnnouncement(Base, BaseModel):
    __tablename__ = 'SysAnnouncement'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    author = Column(Integer, ForeignKey('UserInfo.id'), nullable=False)
    is_visible = Column(Integer, default=True)
