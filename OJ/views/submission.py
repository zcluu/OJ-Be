from threading import Thread

from fastapi import APIRouter, Depends, Header, status, Response
from fastapi_pagination import Params, paginate

from sqlalchemy.orm import Session

from OJ.util.aes import AESTool
from OJ.db.database import get_session, SessionLocal

from OJ.util.controller import get_user
from OJ.util.judge import JudgeDispatcher
from OJ.util.constant import JudgeStatus
from OJ.util.schedule import *

from OJ.models import Submission, ProblemInfo, ContestProblem

from typing import Union

router = APIRouter(
    prefix='/api/submission',
    tags=['submissions']
)


@router.post("/judge")
async def judge(form: JudgeForm, x_token: Union[str, None] = Header(None), db: Session = Depends(get_session)):
    pid = AESTool.decrypt_data(form.pid)
    problem = db.query(ProblemInfo).filter_by(id=pid).first()
    if not problem:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    language = form.language
    user = get_user(x_token)
    user_id = user.id
    code_source = form.source_code
    if form.cp_id != '':
        cp = db.query(ContestProblem).filter_by(id=AESTool.decrypt_data(form.cp_id), pid=pid).first()
        if cp:
            cid = cp.cid
        else:
            cid = None
    else:
        cid = None
    submission = Submission(language=language,
                            user_id=user_id,
                            code_source=code_source,
                            problem_id=pid,
                            contest_id=cid)
    db.add(submission)
    db.commit()
    thread = Thread(target=SubmissionJudge, args=(submission.id, pid))
    thread.start()
    # JudgeDispatcher(submission.id, problem.id, db).judge()
    return submission.id


def SubmissionJudge(sid, pid):
    sess = SessionLocal()
    dis = JudgeDispatcher(sid, pid, sess)
    dis.judge()


@router.get("/status")
async def submission_status(submission_id: int,
                            db: Session = Depends(get_session)):
    submission = db.query(Submission).filter_by(id=submission_id).first()
    if not submission:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    if submission.result in (JudgeStatus.PENDING, JudgeStatus.JUDGING):
        return {
            'result': submission.result
        }
    else:
        return submission.to_dict()


@router.get("/problem")
async def submission_problem(pid: str, db: Session = Depends(get_session), params: Params = Depends()):
    pid = AESTool.decrypt_data(pid)
    submissions = db.query(Submission).filter_by(problem_id=pid).all()
    response = []
    for sub in submissions:
        response.append(sub.to_dict(['id', 'create_time', 'result', 'language']))
    return paginate(response, params)
