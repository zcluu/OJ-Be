from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float
import datetime

from OJ.db.database import Base, BaseModel


class JudgeServer(Base, BaseModel):
    __tablename__ = 'JudgerServer'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip = Column(String(50), nullable=True)
    port = Column(String(50))
    hostname = Column(String(50))
    judger_version = Column(String(50))
    cpu_core = Column(Integer)
    memory_usage = Column(Float)
    cpu_usage = Column(Float)
    last_heartbeat = Column(DateTime)
    create_time = Column(DateTime, default=datetime.datetime.now)
    task_number = Column(Integer, default=0)
    service_url = Column(String(100))
    is_disabled = Column(Boolean, default=False)

    @property
    def status(self):
        # 增加一秒延时，提高对网络环境的适应性
        # if (datetime.datetime.now() - self.last_heartbeat).seconds > 6:
        #     return "abnormal"
        return "normal"
