from fastapi import APIRouter, Depends, Header, status, Response

from sqlalchemy.orm import Session

from OJ.db.database import get_session
from OJ.util.controller import get_user
from OJ.util.judge import JudgeDispatcher
from OJ.util.constant import JudgeStatus, CONTEST_TYPE
from OJ.util.schedule import *
from OJ.models import Submission, ProblemInfo, ContestInfo

from fastapi_pagination import Page, paginate
from typing import Union

router = APIRouter(
    prefix='/api/contest',
    tags=['contest']
)


@router.get('/recent')
async def get_recent(db: Session = Depends(get_session)):
    contests = db.query(ContestInfo).filter_by(contest_type=CONTEST_TYPE.NORMAL).order_by('start_at').limit(5).all()
    result = []
    for it in contests:
        dic = it.to_dict()
        dic['status'] = it.status
        del dic['contest_type']
        del dic['created_by']
        del dic['password']
        del dic['only_id']
        dic['admin'] = it.user.username
        dic['rule'] = 'ACM' if dic['rule'] == 0 else 'OI'
        result.append(dic)
    return result


@router.get('/all')
async def get_all(db: Session = Depends(get_session)):
    contests = db.query(ContestInfo).filter_by(contest_type=CONTEST_TYPE.NORMAL).all()

    result = []
    for it in contests:
        dic = it.to_dict()
        dic['status'] = it.status
        del dic['contest_type']
        del dic['created_by']
        del dic['password']
        del dic['only_id']
        dic['admin'] = it.user.username
        dic['rule'] = 'ACM' if dic['rule'] == 0 else 'OI'
        result.append(dic)
    return result
