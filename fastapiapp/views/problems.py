from fastapi import Request, UploadFile, File, APIRouter

import os

from fastapiapp.util.common import rand_str
from fastapiapp.util.zip_processor import TestCaseZipProcessor

router = APIRouter(
    prefix='/api/problem',
    tags=['problems']
)


@router.post("/upload/testcases")
async def api_upload_testcases(file: UploadFile = File(...), spj=False):
    tmp_file = f"tmp/{rand_str()}.zip"
    with open(tmp_file, "wb") as f:
        content = await file.read()
        f.write(content)
    zip_process = TestCaseZipProcessor()
    spj = spj == 'true'
    info, test_case_id = zip_process.process_zip(tmp_file, spj=spj)
    os.remove(tmp_file)
    return {"id": test_case_id, "info": info, "spj": spj}
