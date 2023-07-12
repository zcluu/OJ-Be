from typing import Optional, Any, Union
from OJ.models.UserModels import UserSession, UserInfo

from sqlalchemy.orm import Session
from OJ.db.database import engine


def get_user(token) -> UserInfo:
    with Session(engine) as session:
        session.begin()
        sess = session.query(UserSession).filter(UserSession.token == token).first()
        if not sess:
            return UserInfo()
        user = sess.sess2user
        session.close()
        return user
