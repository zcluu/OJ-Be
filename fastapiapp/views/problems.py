from fastapi import Request, UploadFile, File, APIRouter

import os

from fastapiapp.util.common import rand_str
from fastapiapp.util.zip_processor import TestCaseZipProcessor
from fastapiapp.config.config import PROJECT_PATH

from glob import glob

router = APIRouter(
    prefix='/api/problem',
    tags=['problems']
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
