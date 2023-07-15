from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime

from OJ.db.database import Base, BaseModel
from OJ.util.common import hash256
from OJ.util.constant import *


class Submission(Base, BaseModel):
    __tablename__ = 'Submission'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    language = Column(String(30))
    contest_id = Column(Integer, ForeignKey('ContestInfo.id'))
    problem_id = Column(Integer, ForeignKey('ProblemInfo.id'))
    create_time = Column(DateTime, default=datetime.datetime.now)
    code_source = Column(String(5000), nullable=False)
    result = Column(Integer, default=JudgeStatus.PENDING)
    info = Column(JSON, default={})  # judger response
    statistic_info = Column(JSON, default={})

    _user = relationship('UserInfo', backref='submissions')
    _contest = relationship('ContestInfo', backref='submissions')
    _problem = relationship('ProblemInfo', backref='submissions')

    @property
    def user(self):
        return self._user

    @property
    def problem(self):
        return self._problem

    @property
    def contest(self):
        return self._contest

    @property
    def is_ac(self):
        return self.result == JudgeStatus.ACCEPTED



