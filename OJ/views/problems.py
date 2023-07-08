from typing import Union

from fastapi import Request, UploadFile, File, APIRouter, Depends, Header
from fastapi.responses import JSONResponse

import os
import requests
from sqlalchemy import desc

from sqlalchemy.orm import Session

from OJ.app.settings import PROJECT_PATH, JUDGER_SERVER

from OJ.models import UserInfo
from OJ.db.database import get_session
from OJ.util.common import rand_str
from OJ.util.controller import get_user
from OJ.util.zip_processor import TestCaseZipProcessor

from OJ.util.schedule import *

from OJ.models.ProblemModels import ProblemInfo, UserProblemStatus

from fastapi_pagination import Page, Params, paginate

router = APIRouter(
    prefix='/api/problem',
    tags=['problems']
)


@router.get("/hot")
async def problem_hot(db: Session = Depends(get_session)):
    problems = db.query(ProblemInfo).filter_by(status=0).order_by(desc(ProblemInfo.submission_count)).limit(5).all()
    result = []
    for pro in problems:
        result.append({
            'id': pro.id,
            'title': pro.title,
            'submission': pro.submission_count,
            'ac_count': pro.ac_count,
            'ac_rate': 0 if pro.ac_count == 0 else (pro.ac_count / pro.submission_count) * 100
        })
    return result


@router.get("/all")
async def problem_all(db: Session = Depends(get_session), params: Params = Depends()):
    problems = db.query(ProblemInfo).filter_by(status=0).all()
    result = []
    for pro in problems:
        result.append({
            'id': pro.id,
            'title': pro.title,
            'submission': pro.submission_count,
            'ac_count': pro.ac_count,
            'ac_rate': 0 if pro.ac_count == 0 else (pro.ac_count / pro.submission_count) * 100
        })
    return paginate(result, params)


@router.get("/detail")
async def problem_detail(problem_id, x_token: Union[str, None] = Header(None), db: Session = Depends(get_session)):
    problem_id = problem_id
    problem = db.query(ProblemInfo).filter_by(id=problem_id).first()
    if not problem:
        return JSONResponse({
            'msg': '问题不存在，异常访问'
        }, status_code=404)
    user = get_user(x_token)
    response = problem.to_dict()
    response['samples'] = [(it.split('|||')[0], it.split('|||')[1]) for it in response['samples'].split('+#+#')]
    response['language'] = response['language'].split('###')
    response['created_by'] = problem.user.username
    status = db.query(UserProblemStatus).filter_by(user_id=user.id, problem_id=problem_id).first()
    if status:
        status = status.to_dict(['is_ac', 'score', 'submission'])
        if status['submission']:
            status['submission'] = status['submission'].to_dict(['result'])
    response['status'] = status
    return response


@router.post("/create")
async def problem_create(form: ProblemForm, db: Session = Depends(get_session)):
    problem = ProblemInfo(
        title=form.title,
        description=form.description,
        inputs=form.inputs,
        outputs=form.outputs,
        samples=form.samples,
        hints=form.hints,
        source=form.source,
        is_spj=form.is_spj,
        test_id=form.test_id,
        time_limit=form.time_limit,
        memory_limit=form.memory_limit,
        io_mode=form.io_mode,
    )
    db.add(problem)
    db.commit()
    return problem.to_dict()


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


@router.get("/testcase")
async def problem_get_testcase(testcase_id):
    path = os.path.join(PROJECT_PATH, 'testcases', testcase_id)
    files = os.listdir(path)
    inputs = [it for it in files if it.endswith('.in')]
    outputs = [it for it in files if it.endswith('.out')]
    count = len(files)
    return {
        'count': count,
        'inputs': inputs,
        'outputs': outputs
    }
