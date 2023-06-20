from fastapi import APIRouter, Depends, Header, status, Response

from sqlalchemy.orm import Session

from OJ.db.database import get_session

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
async def judge(form: JudgeForm, token: Union[str, None] = Header(None), db: Session = Depends(get_session)):
    problem = db.query(ProblemInfo).filter_by(id=form.problem_id).first()
    if not problem:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    language = form.language
    user = get_user(token)
    user_id = user.id
    code_source = form.source_code
    submission = Submission(language=language,
                            user_id=user_id,
                            code_source=code_source,
                            problem_id=form.problem_id,
                            contest_id=problem.contest_id)
    db.add(submission)
    db.commit()
    JudgeDispatcher(submission.id, problem.id).judge()


@router.get("/status")
async def submission_status(submission_id: int,
                            token: Union[str, None] = Header(None),
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
