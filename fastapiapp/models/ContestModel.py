from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

from fastapiapp.db.database import Base, BaseModel
from fastapiapp.util.common import hash256


class ContestInfo(Base, BaseModel):
    __tablename__ = 'ContestInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    title = Column(String(200), nullable=False)
    description = Column(String(5000), nullable=False)  # Description
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    # 0-->Normal 1-->Password Protected
    # 2-->Hidden but available(visit by invitation URL)
    # 3-->Hidden and unavailable
    contest_type = Column(Integer, default=0)
    password = Column(String(30), default='')  # needed if contest_type==1
    only_id = Column(String(50), default='')  # needed if contest_type==2
    rule = Column(Integer, default=0)  # 0-->ACM 1-->OI
    created_by = Column(Integer, ForeignKey('UserInfo.id'))
    _user = relationship('UserInfo', backref='contests')


class Announcement(Base, BaseModel):
    __tablename__ = 'Announcement'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(String(5000), nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now)
    update_time = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    contest = Column(Integer, ForeignKey('ContestInfo.id'), nullable=False)
    author = Column(Integer, ForeignKey('UserInfo.id'), nullable=False)
    is_visible = Column(Integer, default=True)
    _contest = relationship('ContestInfo', backref='announcements')
