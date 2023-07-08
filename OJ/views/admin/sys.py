import hashlib
import json
import time
import zipfile
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
    prefix='/api/admin/sys',
    tags=['system control']
)


@router.post('/qdu/export')
async def qdu_export(file: UploadFile = File(...), db: Session = Depends(get_session)):
    tmp_file = f"tmp/{rand_str()}.zip"
    with open(tmp_file, "wb") as f:
        content = await file.read()
        f.write(content)
    try:
        zip_file = zipfile.ZipFile(tmp_file, "r")
    except zipfile.BadZipFile as e:
        print(e)
        return Response("Bad zip file", status.HTTP_500_INTERNAL_SERVER_ERROR)
    files = zip_file.namelist()
    dic = {}
    for f in files:
        tid = f.split('/')[0]
        dic[tid] = dic.get(tid, {})
        if '.json' in f:
            dic[tid]['problem'] = f
        else:
            dic[tid]['testcase'] = dic[tid].get('testcase', [])
            dic[tid]['testcase'].append(f)
    null = None
    problems = []
    for tid, val in dic.items():
        problem_info = eval(zip_file.read(val['problem']).decode())
        title = problem_info['title']
        description = problem_info['description']['value']
        time_limit = problem_info['time_limit']
        memory_limit = problem_info['memory_limit']
        samples = problem_info['samples']
        is_spj = problem_info['spj'] is not None
        mode = 0 if problem_info['rule_type'] == 'ACM' else 1
        test_case_score = {str(ix): it['score'] for ix, it in enumerate(problem_info['test_case_score'])}
        total_score = sum([it['score'] for it in problem_info['test_case_score']])
        source = problem_info['source']
        inputs = problem_info['input_description']['value']
        outputs = problem_info['output_description']['value']
        hint = problem_info['hint']['value']
        samples = '+#+#'.join([it['input'] + '|||' + it['output'] for it in samples])
        problem = ProblemInfo(
            title=title,
            language='cxx###c###py3###php',
            description=description,
            inputs=inputs,
            outputs=outputs,
            time_limit=time_limit,
            memory_limit=memory_limit,
            samples=samples,
            is_spj=is_spj,
            mode=mode,
            test_case_score=test_case_score,
            total_score=total_score,
            source=source,
            hints=hint,
            created_by=4,
        )
        test_case_id = rand_str()
        test_case_dir = os.path.join('testcases', test_case_id)
        os.mkdir(test_case_dir)
        os.chmod(test_case_dir, 0o710)
        size_cache = {}
        md5_cache = {}
        test_case_list = val['testcase']
        for item in test_case_list:
            file_name = item.split('/')[-1]
            with open(os.path.join(test_case_dir, file_name), "wb") as f:
                content = zip_file.read(f"{item}").replace(b"\r\n", b"\n")
                size_cache[file_name] = len(content)
                if file_name.endswith(".out"):
                    md5_cache[file_name] = hashlib.md5(content.rstrip()).hexdigest()
                f.write(content)
        test_case_info = {"spj": is_spj, "test_cases": {}}

        info = []
        test_case_list = [it.split('/')[-1] for it in test_case_list]
        if is_spj:
            for index, item in enumerate(test_case_list):
                data = {"input_name": item, "input_size": size_cache[item]}
                info.append(data)
                test_case_info["test_cases"][str(index + 1)] = data
        else:
            # ["1.in", "1.out", "2.in", "2.out"] => [("1.in", "1.out"), ("2.in", "2.out")]
            test_case_list = zip(*[test_case_list[i::2] for i in range(2)])
            for index, item in enumerate(test_case_list):
                data = {"stripped_output_md5": md5_cache[item[1]],
                        "input_size": size_cache[item[0]],
                        "output_size": size_cache[item[1]],
                        "input_name": item[0],
                        "output_name": item[1]}
                info.append(data)
                test_case_info["test_cases"][str(index + 1)] = data

        with open(os.path.join(test_case_dir, "info"), "w", encoding="utf-8") as f:
            f.write(json.dumps(test_case_info, indent=4))

        for item in os.listdir(test_case_dir):
            os.chmod(os.path.join(test_case_dir, item), 0o640)
        problem.test_id = test_case_id
        db.add(problem)
    db.commit()
    return True
