from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

from fastapiapp.db.database import Base, BaseModel
from fastapiapp.util.common import hash256


class ProblemInfo(Base, BaseModel):
    __tablename__ = 'ProblemInfo'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(5000), nullable=False)  # Description
    inputs = Column(String(5000), nullable=False)  # Input
    outputs = Column(String(5000), nullable=False)  # Output
    # sample input1|||sample output1+#+#sample input2|||sample output2
    samples = Column(String(5000), nullable=False, default='')
    hints = Column(String(5000), default='')
    source = Column(String(5000), default='')
    is_spj = Column(Boolean, default=False)
    test_id = Column(String(50))
    ac_count = Column(Integer, default=0)
    wa_count = Column(Integer, default=0)
    time_limit = Column(Integer, default=1000)  # ms
    memory_limit = Column(Integer, default=512 * 1024 * 1024)  # byte
    io_mode = Column(Integer, default=0)  # 0-->normal judge 1-->special judge
    # 0-->show 1-->hide
    # 2-->contest mode but hide
    # 3-->contest mode but show
    status = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('UserInfo.id'))
    contest = Column(Integer, ForeignKey('ContestInfo.id'))
    _user = relationship('UserInfo', backref='problems')
    _contest = relationship('ContestInfo', backref='problems')
