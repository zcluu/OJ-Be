import time
from typing import Union

from fastapi import Request, UploadFile, File, APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse, Response

import os
import requests
from sqlalchemy import desc

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from OJ.app.settings import PROJECT_PATH, JUDGER_SERVER

from OJ.models import UserInfo
from OJ.db.database import get_session
from OJ.util.aes import AESTool
from OJ.util.common import rand_str, hash256
from OJ.util.controller import get_user
from OJ.util.zip_processor import TestCaseZipProcessor

from OJ.util.schedule import *

from OJ.models import ContestInfo, ProblemInfo, UserProblemStatus, ContestProblem

from fastapi_pagination import Page, Params, paginate

router = APIRouter(
    prefix='/api/admin/problem',
    tags=['admin problems']
)


@router.delete('')
async def delete_problem(pid: str, db: Session = Depends(get_session)):
    pid = AESTool.decrypt_data(pid)
    pid = AESTool.decrypt_data(pid)
    pro = db.query(ProblemInfo).filter_by(id=pid).first()
    if not pro:
        return Response('Problem not found', status_code=status.HTTP_404_NOT_FOUND)
    db.delete(pro)
    db.commit()
    return True


@router.get("/all")
async def contest_all(db: Session = Depends(get_session), params: Params = Depends()):
    problems = db.query(ProblemInfo).filter(or_(ProblemInfo.status == 0, ProblemInfo.status == 1)).all()
    result = []
    for pro in problems:
        result.append({
            'id': pro.id,
            'title': pro.title,
            'author': pro.user('username'),
            'create_time': pro.create_time,
            'status': pro.status == 0
        })
    return paginate(result, params)


@router.post("/upload/testcases")
async def problem_upload_testcases(file: UploadFile = File(...), spj=False):
    tmp_file = f"tmp/{rand_str()}.zip"
    with open(tmp_file, "wb") as f:
        content = await file.read()
        f.write(content)
    zip_process = TestCaseZipProcessor()
    spj = spj == 'true'
    info, test_case_id = zip_process.process_zip(tmp_file, spj=spj)
    os.remove(tmp_file)
    return {"id": test_case_id, "info": info, "spj": spj}


@router.post("/update")
async def problem_update(problem: ProblemForm, db: Session = Depends(get_session)):
    pro = db.query(ProblemInfo).filter_by(id=problem.id).first()
    if not pro:
        return Response('Problem not found', status_code=status.HTTP_404_NOT_FOUND)
    pro.title = problem.title
    pro.description = problem.description
    pro.inputs = problem.inputs
    pro.outputs = problem.outputs
    pro.samples = '+#+#'.join(['|||'.join(it) for it in problem.samples])
    pro.language = '###'.join([it for it in problem.language if it in ['c', 'cxx', 'py3', 'py2', 'php', 'go', 'js']])
    pro.mode = problem.mode
    pro.is_spj = problem.is_spj
    pro.source = problem.source
    pro.time_limit = problem.time_limit
    pro.memory_limit = problem.memory_limit
    pro.hints = problem.hints
    pro.test_id = problem.test_id
    db.commit()
    return True


@router.post("/add")
async def problem_add(problem: ProblemForm, x_token: Union[str, None] = Header(None),
                      db: Session = Depends(get_session)):
    if problem.cid != '':
        try:
            cid = AESTool.decrypt_data(problem.cid)
        except:
            return Response('Invalid Request', status_code=status.HTTP_400_BAD_REQUEST)
    else:
        cid = None
    pro = ProblemInfo()
    pro.title = problem.title
    pro.description = problem.description
    pro.inputs = problem.inputs
    pro.outputs = problem.outputs
    pro.samples = '+#+#'.join(['|||'.join(it) for it in problem.samples])
    pro.language = '###'.join([it for it in problem.language if it in ['c', 'cxx', 'py3', 'py2', 'php', 'go', 'js']])
    pro.mode = problem.mode
    pro.is_spj = problem.is_spj
    pro.source = problem.source
    pro.time_limit = problem.time_limit
    pro.memory_limit = problem.memory_limit
    pro.hints = problem.hints
    pro.test_id = problem.test_id
    pro.created_by = get_user(x_token).id
    pro.contest_id = cid

    db.add(pro)
    db.commit()

    cp = ContestProblem(cid=cid, pid=pro.id)
    db.add(cp)
    db.commit()

    return True


@router.get("/visible")
async def problem_visible(pid: str, s=None, db: Session = Depends(get_session)):
    pid = AESTool.decrypt_data(pid)
    pro = db.query(ProblemInfo).filter_by(id=pid).first()
    if not pro:
        return Response('Problem not found', status_code=status.HTTP_404_NOT_FOUND)
    if s:
        pro.status = None
    else:
        if pro.status == 0:
            pro.status = 1
        elif pro.status == 1:
            pro.status = 0
    db.commit()
    return True
