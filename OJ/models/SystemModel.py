from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, JSON
import datetime

from OJ.db.database import Base, BaseModel


class SysAnnouncement(Base, BaseModel):
    __tablename__ = 'SysAnnouncement'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    author = Column(Integer, ForeignKey('UserInfo.id'), nullable=False)
    is_visible = Column(Integer, default=True)
