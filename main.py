import os

from fastapi import FastAPI, UploadFile, File
from starlette.middleware.cors import CORSMiddleware
from util.zip_processor import TestCaseZipProcessor

from util.common import rand_str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/testcases")
async def upload_testcases(file: UploadFile = File(...), spj=False):
    tmp_file = f"tmp/{rand_str()}.zip"
    with open(tmp_file, "wb") as f:
        content = await file.read()
        f.write(content)
    zip_process = TestCaseZipProcessor()
    spj = spj == 'true'
    info, test_case_id = zip_process.process_zip(tmp_file, spj=spj)
    os.remove(tmp_file)
    return {"id": test_case_id, "info": info, "spj": spj}
