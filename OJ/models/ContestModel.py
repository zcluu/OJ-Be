from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, BigInteger
from sqlalchemy.orm import relationship
import datetime

from OJ.util.constant import ContestStatus
from OJ.db.database import Base, BaseModel


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
    password = Column(String(100), default='')  # needed if contest_type==1
    only_id = Column(String(50), default='')  # needed if contest_type==2
    rule = Column(Integer, default=0)  # 0-->ACM 1-->OI
    created_by = Column(Integer, ForeignKey('UserInfo.id'))
    _user = relationship('UserInfo', backref='contests')

    @property
    def status(self):
        if self.start_at > datetime.datetime.now():
            # 没有开始 返回1
            return ContestStatus.CONTEST_NOT_START
        elif self.end_at < datetime.datetime.now():
            # 已经结束 返回-1
            return ContestStatus.CONTEST_ENDED
        else:
            # 正在进行 返回0
            return ContestStatus.CONTEST_UNDERWAY

    def user(self, filed=None):
        if not filed:
            return self._user
        else:
            return getattr(self._user, filed)


class ContestProblem(Base, BaseModel):
    __tablename__ = 'ContestProblem'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cid = Column(Integer, ForeignKey('ContestInfo.id'), nullable=False)
    pid = Column(Integer, ForeignKey('ProblemInfo.id'), nullable=False)
    is_visible = Column(Boolean, default=True)
    _contest = relationship('ContestInfo', backref='cps')
    _problem = relationship('ProblemInfo', backref='cps')

    @property
    def contest(self):
        return self._contest

    @property
    def problem(self):
        return self._problem


class ACMRank(Base, BaseModel):
    __tablename__ = 'ACMRank'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    cp_id = Column(Integer, ForeignKey('ContestProblem.id'))
    submission_id = Column(Integer, ForeignKey('Submission.id'))
    submission_number = Column(Integer, default=0)  # tries

    total_time = Column(BigInteger, default=0)
    is_ac = Column(Boolean, default=False)
    is_first_ac = Column(Boolean, default=False)
    ac_time = Column(Integer, default=0)

    _user = relationship('UserInfo', backref='acm_ranks')
    _cp = relationship('ContestProblem', backref='acm_rank')
    _submission = relationship('Submission')

    def user(self, filed=None):
        if not filed:
            return self._user
        else:
            return getattr(self._user, filed)

    @property
    def cp(self) -> ContestProblem:
        return self._cp

    @property
    def contest(self) -> ContestInfo:
        return self.cp.contest

    @property
    def problem(self):
        return self.cp.problem


class OIRank(Base, BaseModel):
    __tablename__ = 'oi_rank'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    cp_id = Column(Integer, ForeignKey('ContestProblem.id'))
    submission_id = Column(Integer, ForeignKey('Submission.id'))
    submission_number = Column(Integer, default=0)  # tries

    total_score = Column(Integer, default=0)
    is_ac = Column(Boolean, default=False)
    ac_time = Column(Integer, default=0)

    _user = relationship('UserInfo', backref='oi_ranks')
    _cp = relationship('ContestProblem', backref='oi_rank')
    _submission = relationship('Submission')

    @property
    def user(self):
        return self._user

    @property
    def cp(self) -> ContestProblem:
        return self._cp

    @property
    def contest(self) -> ContestInfo:
        return self.cp.contest

    @property
    def problem(self):
        return self.cp.problem

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
    _user = relationship('UserInfo', backref='contest_announcements')

    def user(self, filed=None):
        if not filed:
            return self._user
        else:
            return getattr(self._user, filed)
