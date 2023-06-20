from fastapi import Request, UploadFile, File, APIRouter, Depends
from fastapi.responses import JSONResponse

import os
import requests

from sqlalchemy.orm import Session

from OJ.app.settings import PROJECT_PATH, JUDGER_SERVER

from OJ.models import UserInfo
from OJ.db.database import get_session
from OJ.util.common import rand_str
from OJ.util.zip_processor import TestCaseZipProcessor

from OJ.util.schedule import *

from OJ.models.ProblemModels import ProblemInfo

router = APIRouter(
    prefix='/api/problem',
    tags=['problems']
)


@router.post("/detail/:problem_id")
async def problem_detail(problem_id, db: Session = Depends(get_session)):
    problem_id = problem_id
    problem = db.query(ProblemInfo).filter_by(id=problem_id).first()
    if not problem:
        return JSONResponse({
            'msg': '问题不存在，异常访问'
        }, status_code=404)
    return problem.to_dict()


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
