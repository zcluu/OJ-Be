from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
import datetime

from OJ.util.constant import ContestStatus
from OJ.db.database import Base, BaseModel
from OJ.util.common import hash256


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

    @property
    def status(self):
        if self.start_at > datetime.datetime.now():
            # 没有开始 返回1
            return ContestStatus.CONTEST_NOT_START
        elif self.start_at < datetime.datetime.now():
            # 已经结束 返回-1
            return ContestStatus.CONTEST_ENDED
        else:
            # 正在进行 返回0
            return ContestStatus.CONTEST_UNDERWAY

    @property
    def user(self):
        return self._user


class ACMRank(Base, BaseModel):
    __tablename__ = 'ACMRank'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    contest_id = Column(Integer, ForeignKey('ContestInfo.id'))
    problem_id = Column(Integer, ForeignKey('ProblemInfo.id'))
    submission_id = Column(Integer, ForeignKey('Submission.id'))
    submission_number = Column(Integer, default=0)  # tries
    error_number = Column(Integer, default=0)
    accepted_number = Column(Integer, default=0)
    total_time = Column(BigInteger, default=0)
    is_ac = Column(Boolean, default=False)
    is_first_ac = Column(Boolean, default=False)
    ac_time = Column(Integer, default=0)

    _user = relationship('UserInfo', backref='acm_ranks')
    _contest = relationship('ContestInfo', backref='acm_ranks')
    _submission = relationship('Submission')


class OIRank(Base, BaseModel):
    __tablename__ = 'oi_rank'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    contest_id = Column(Integer, ForeignKey('ContestInfo.id'))
    problem_id = Column(Integer, ForeignKey('ProblemInfo.id'))
    submission_id = Column(Integer, ForeignKey('Submission.id'))
    submission_number = Column(Integer, default=0)  # tries

    error_number = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    is_ac = Column(Boolean, default=False)
    ac_time = Column(Integer, default=0)

    _user = relationship('UserInfo', backref='oi_ranks')
    _contest = relationship('ContestInfo', backref='oi_ranks')
    _submission = relationship('Submission')

    @property
    def user(self):
        return self._user

    @property
    def contest(self):
        return self._contest

    @property
    def submission(self):
        return self._submission


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
