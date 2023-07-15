from fastapi import APIRouter, Depends, Header, status, Response

from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from OJ.db.database import get_session
from OJ.util.controller import get_user
from OJ.util.judge import JudgeDispatcher
from OJ.util.constant import JudgeStatus, CONTEST_TYPE, ContestRuleType
from OJ.util.schedule import *
from OJ.models import Submission, ProblemInfo, ContestInfo, Announcement, ACMRank, ContestProblem
from OJ.util.aes import AESTool

from fastapi_pagination import Page, paginate, Params
from typing import Union

router = APIRouter(
    prefix='/api/contest',
    tags=['contest']
)


@router.get('/recent')
async def get_recent(db: Session = Depends(get_session)):
    contests = db.query(ContestInfo).filter_by(contest_type=CONTEST_TYPE.NORMAL).order_by('start_at').limit(5).all()
    result = []
    for it in contests:
        dic = it.to_dict()
        dic['status'] = it.status
        del dic['contest_type']
        del dic['created_by']
        del dic['password']
        del dic['only_id']
        dic['admin'] = it.user('username')
        dic['rule'] = 'ACM' if dic['rule'] == 0 else 'OI'
        result.append(dic)
    return result


@router.get('/all')
async def get_all(db: Session = Depends(get_session), params: Params = Depends()):
    contests = db.query(ContestInfo).filter_by(contest_type=CONTEST_TYPE.NORMAL).all()

    result = []
    for it in contests:
        dic = it.to_dict([
            'title', 'description', 'start_at', 'end_at', 'rule', 'status'
        ])
        dic['admin'] = it.user('username')
        dic['rule'] = 'ACM' if dic['rule'] == 0 else 'OI'
        result.append(dic)
    return paginate(result, params)


@router.get('/detail')
async def get_detail(contest_id, db: Session = Depends(get_session)):
    def get_problem_info(cp: ContestProblem):
        pro = cp.problem
        dic = pro.to_dict(['pid', 'title', 'submission_count', 'ac_count', ])
        dic['ac_rate'] = 0 if pro.ac_count == 0 else (pro.ac_count / pro.submission_count) * 100
        dic['cp_id'] = AESTool.encrypt_data(cp.id)
        return dic

    contest = db.query(ContestInfo).filter_by(id=contest_id).first()

    if not contest:
        return JSONResponse({
            'msg': '比赛不存在，异常访问'
        }, status_code=status.HTTP_404_NOT_FOUND)
    response = contest.to_dict([
        'id', 'title', 'description', 'start_at', 'end_at', 'rule', 'status'
    ])
    cps = db.query(ContestProblem).filter_by(cid=contest.id).all()
    problems = [get_problem_info(it) for it in cps]
    response['problems'] = problems
    return response


@router.get('/announcements')
async def get_announcements(contest_id, db: Session = Depends(get_session)):
    announcements = db.query(Announcement).filter_by(contest=contest_id).order_by('update_time').all()
    response = []
    for it in announcements:
        dic = it.to_dict([
            'id', 'title', 'content', 'create_time', 'update_time'
        ])
        dic['author'] = it.user('username')
        response.append(dic)
    return response


@router.get('/rank')
async def get_rank(cid, db: Session = Depends(get_session), params: Params = Depends()):
    contest = db.query(ContestInfo).filter_by(id=cid).first()

    if not contest:
        return JSONResponse({
            'msg': '比赛不存在，异常访问'
        }, status_code=status.HTTP_404_NOT_FOUND)
    cps = db.query(ContestProblem).filter_by(cid=cid).all()
    problems = [cp.problem for cp in cps]
    problems_id = {it.id: ix for ix, it in enumerate(problems)}
    usernames = []
    u_result = {}
    u_rank = {}
    cps = db.query(ContestProblem).filter_by(cid=cid).all()
    if contest.rule == ContestRuleType.ACM:
        ranks = [cp.acm_rank for cp in cps]
        for rank in ranks:
            username = rank.user('username')
            usernames.append(username)
            u_rank[username] = u_rank.get(username, [])
            u_rank[username].append(rank)
            u_result[username] = u_result.get(username, {})
            u_result[username]['submissions'] = u_result[username].get('submissions',
                                                                       [{} for _ in range(len(problems))])
            u_result[username]['problems'] = u_result[username].get('problems', [0 for _ in range(len(problems))])
            u_result[username]['problems'][problems_id[rank.problem_id]] = 1
            u_result[username]['submission_count'] = u_result[username].get('submission_count', 0) + \
                                                     rank.submission_number

            u_result[username]['ac_count'] = u_result[username].get('ac_count', 0) + rank.is_ac
            u_result[username]['total_time'] = u_result[username].get('total_time', 0)
            if rank.is_ac:
                u_result[username]['total_time'] += rank.total_time
                u_result[username]['is_ac'] = True
            else:
                u_result[username]['is_ac'] = False
            u_result[username]['submissions'][problems_id[rank.problem_id]]['total_time'] = rank.total_time
            u_result[username]['submissions'][problems_id[rank.problem_id]]['is_ac'] = rank.is_ac
            u_result[username]['submissions'][problems_id[rank.problem_id]]['is_first_ac'] = rank.is_first_ac
            u_result[username]['submissions'][problems_id[rank.problem_id]][
                'submission_number'] = rank.submission_number
    response = []
    for key, val in u_result.items():
        dic = {'username': key}
        dic.update(val)
        response.append(dic)
    response.sort(key=lambda x: (-x['ac_count'], x['total_time'], x['username']))
    return {'ranks': paginate(response, params), 'length': len(cps)}
