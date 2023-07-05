from threading import Thread

from fastapi import APIRouter, Depends, Header, status, Response
from fastapi_pagination import Params, paginate

from sqlalchemy.orm import Session

from OJ.db.database import get_session, SessionLocal

from OJ.util.controller import get_user
from OJ.util.judge import JudgeDispatcher
from OJ.util.constant import JudgeStatus
from OJ.util.schedule import *

from OJ.models import Submission, ProblemInfo

from typing import Union

router = APIRouter(
    prefix='/api/submission',
    tags=['submissions']
)


@router.post("/judge")
async def judge(form: JudgeForm, x_token: Union[str, None] = Header(None), db: Session = Depends(get_session)):
    problem = db.query(ProblemInfo).filter_by(id=form.problem_id).first()
    if not problem:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    language = form.language
    user = get_user(x_token)
    user_id = user.id
    code_source = form.source_code
    submission = Submission(language=language,
                            user_id=user_id,
                            code_source=code_source,
                            problem_id=form.problem_id,
                            contest_id=problem.contest_id)
    db.add(submission)
    db.commit()
    thread = Thread(target=SubmissionJudge, args=(submission.id, problem.id))
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
async def submission_problem(pid: int, db: Session = Depends(get_session), params: Params = Depends()):
    submissions = db.query(Submission).filter_by(problem_id=pid).all()
    response = []
    for sub in submissions:
        response.append(sub.to_dict(['id', 'create_time', 'result', 'language']))
    return paginate(response, params)
