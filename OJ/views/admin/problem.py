import time
from typing import Union

from fastapi import Request, UploadFile, File, APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse, Response

import os
import requests
from sqlalchemy import desc

from sqlalchemy.orm import Session

from OJ.app.settings import PROJECT_PATH, JUDGER_SERVER

from OJ.models import UserInfo
from OJ.db.database import get_session
from OJ.util.common import rand_str, hash256
from OJ.util.controller import get_user
from OJ.util.zip_processor import TestCaseZipProcessor

from OJ.util.schedule import *

from OJ.models.ProblemModels import ProblemInfo, UserProblemStatus

from fastapi_pagination import Page, Params, paginate

router = APIRouter(
    prefix='/api/admin/problem',
    tags=['admin problems']
)


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
