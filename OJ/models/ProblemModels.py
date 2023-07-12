from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime

from OJ.db.database import Base, BaseModel
from OJ.util.aes import AESTool
from OJ.util.constant import ContestStatus
from OJ.util.common import hash256


class ProblemInfo(Base, BaseModel):
    __tablename__ = 'ProblemInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)  # Description
    inputs = Column(Text, nullable=False)  # Input
    outputs = Column(Text, nullable=False)  # Output
    language = Column(Text, nullable=False)
    # sample input1|||sample output1+#+#sample input2|||sample output2
    samples = Column(Text, nullable=False, default='')
    hints = Column(Text, default='')
    source = Column(Text, default='')
    is_spj = Column(Boolean, default=False)  # normal judge/special judge
    test_id = Column(String(50))
    submission_count = Column(Integer, default=0)
    ac_count = Column(Integer, default=0)
    wa_count = Column(Integer, default=0)
    time_limit = Column(Integer, default=1000)  # ms
    memory_limit = Column(Integer, default=256)  # MB
    mode = Column(Integer, default=0)  # 0-->ACM 1-->OI
    # 0-->show 1-->hide
    # 2-->contest mode but hide
    # 3-->contest mode but show
    status = Column(Integer, default=0)
    test_case_score = Column(JSON, default={})
    total_score = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.datetime.now)
    created_by = Column(Integer, ForeignKey('UserInfo.id'))
    contest_id = Column(Integer, ForeignKey('ContestInfo.id'))
    statistic_info = Column(JSON, default={})
    _user = relationship('UserInfo', backref='problems')
    _contest = relationship('ContestInfo', backref='problems')

    @property
    def contest(self):
        return self._contest

    @property
    def pid(self):
        return AESTool.encrypt_data(self.id)

    def user(self, filed=None):
        if not filed:
            return self._user
        else:
            return getattr(self._user, filed)


class UserProblemStatus(Base, BaseModel):
    __tablename__ = 'UserProblemStatus'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserInfo.id'))
    problem_id = Column(Integer, ForeignKey('ProblemInfo.id'))
    ac_id = Column(Integer, ForeignKey('Submission.id'))  # first ac
    is_ac = Column(Boolean, default=False)
    score = Column(Integer, default=0)  # if problem.mode == OI

    _user = relationship('UserInfo', backref='problems_status')
    _submission = relationship('Submission')
    _problem = relationship('ProblemInfo', backref='users_status')

    @property
    def user(self):
        return self._user

    @property
    def submission(self):
        return self._submission

    @property
    def problem(self):
        return self._problem

    @property
    def is_available(self):
        if not self.problem.contest_id:
            return True
        if self.problem.contest.status != ContestStatus.CONTEST_ENDED:
            return False
        return True
