from typing import Optional, Any, Union
from OJ.models.UserModels import UserSession

from sqlalchemy.orm import Session
from OJ.db.database import engine


def get_user(token) -> Optional[Any]:
    with Session(engine) as session:
        session.begin()
        sess = session.query(UserSession).filter(UserSession.token == token).first()
        user = sess.sess2user
        session.close()
        return user
