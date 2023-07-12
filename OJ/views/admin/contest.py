import datetime
from typing import Union

from fastapi import Request, UploadFile, File, APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from OJ.db.database import get_session
from OJ.util.aes import AESTool
from OJ.util.common import rand_str, hash256
from OJ.util.controller import get_user
from OJ.util.zip_processor import TestCaseZipProcessor

from OJ.util.schedule import *

from OJ.models import ContestInfo, ProblemInfo, UserProblemStatus, ContestProblem

from fastapi_pagination import Page, Params, paginate

router = APIRouter(
    prefix='/api/admin/contest',
    tags=['admin contest']
)


@router.get("/all")
async def contest_all(db: Session = Depends(get_session), params: Params = Depends()):
    contests = db.query(ContestInfo).all()
    result = []
    for con in contests:
        result.append({
            'id': con.id,
            'title': con.title,
            'author': con.user('username'),
            'start_at': con.start_at,
            'end_at': con.end_at,
            'status': con.status
        })
    return paginate(result, params)


@router.get('/detail')
async def get_detail(cid, db: Session = Depends(get_session)):
    cid = AESTool.decrypt_data(cid)
    contest = db.query(ContestInfo).filter_by(id=cid).first()

    if not contest:
        return JSONResponse({
            'msg': '比赛不存在，异常访问'
        }, status_code=status.HTTP_404_NOT_FOUND)
    response = contest.to_dict([
        'id', 'title', 'description', 'start_at', 'end_at', 'rule', 'status', 'contest_type', 'only_id'
    ])
    return response


@router.post("/add")
async def contest_add(form: ContestForm, x_token: Union[str, None] = Header(None), db: Session = Depends(get_session)):
    user = get_user(x_token)
    contest = ContestInfo()
    contest.title = form.title
    contest.description = form.description
    datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    contest.start_at = datetime.datetime.strptime(form.start_at, datetime_format)
    contest.end_at = datetime.datetime.strptime(form.end_at, datetime_format)
    contest.contest_type = form.contest_type
    contest.password = hash256(form.password)
    contest.rule = form.rule
    contest.created_by = user.id
    db.add(contest)
    db.commit()
    contest.only_id = AESTool.encrypt_data(str(contest.id))
    db.commit()


@router.post("/update")
async def contest_update(form: ContestForm, x_token: Union[str, None] = Header(None),
                         db: Session = Depends(get_session)):
    user = get_user(x_token)
    contest = db.query(ContestInfo).filter_by(id=form.id).first()
    if not contest:
        return Response('Invalid Contest ID', status_code=status.HTTP_404_NOT_FOUND)
    db.commit()
    contest.only_id = AESTool.encrypt_data(str(contest.id))
    db.commit()


@router.get("/problem")
async def contest_problem_all(cid, db: Session = Depends(get_session), params: Params = Depends()):
    cid = AESTool.decrypt_data(cid)
    cps = db.query(ContestProblem).filter_by(cid=cid).all()
    problems = []
    for cp in cps:
        pro = cp.problem
        problems.append({
            'id': AESTool.encrypt_data(str(pro.id)),
            'title': pro.title,
            'author': pro.user('username'),
            'create_time': pro.create_time,
            'status': pro.status == 0
        })
    return problems
