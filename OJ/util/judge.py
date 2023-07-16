import hashlib
import json
import logging
from urllib.parse import urljoin

from sqlalchemy.orm import Session
import requests

from OJ.app.settings import *
from OJ.db.database import engine, SessionLocal
from OJ.models import *
from OJ.models.JudgeModel import JudgeServer

logger = logging.getLogger(__name__)


class ChooseJudgeServer:
    def __init__(self, sess=Session(engine)):
        self.server = None
        self.sess = sess

    def __enter__(self) -> [JudgeServer, None]:
        servers = self.sess.query(JudgeServer).filter_by(is_disabled=False).order_by("task_number").all()
        servers = [s for s in servers if s.status == "normal"]
        for server in servers:
            if server.task_number <= server.cpu_core * 2:
                server.task_number = server.task_number + 1
                self.sess.commit()
                self.server = server
                return server
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            self.sess.begin()
            server = self.sess.query(JudgeServer).filter_by(id=self.server.id).first()
            server.task_number = server.task_number - 1
            self.sess.commit()
            self.sess.close()


class DispatcherBase(object):
    def __init__(self):
        self.token = hashlib.sha256(JUDGER_TOKEN.encode()).hexdigest()

    def _request(self, url=JUDGER_SERVER, data=None, language=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token}}
        if data:
            kwargs["json"] = data
        try:
            return requests.post(url, params={
                'language': language
            }, data=data, **kwargs).json()
        except Exception as e:
            logger.exception(e)


class JudgeDispatcher(DispatcherBase):

    def __init__(self, submission_id, problem_id, session=SessionLocal(), cp_id=-1):
        """
        :param submission_id: which submission
        :param problem_id: which problem
        :param db: db_session
        """
        super().__init__()
        self.sess = session
        self.cp_id = cp_id
        if cp_id > 0:
            self.cp = self.sess.query(ContestProblem).filter_by(id=cp_id).first()
        else:
            self.cp = None
        self.submission_id = submission_id

        self.submission = self.sess.query(Submission).filter_by(id=self.submission_id).first()
        self.problem_id = problem_id
        self.contest_id = self.submission.contest_id
        self.last_result = self.submission.result if self.submission.info else None
        # submission.statistic_info
        self.statistic_info = {}

        if self.contest_id:
            self.contest = self.submission.contest
        else:
            self.contest = None
        self.problem = self.submission.problem

    def _compute_statistic_info(self, resp_data):
        # 用时和内存占用保存为多个测试点中最长的那个
        self.statistic_info["time_cost"] = max([x["cpu_time"] for x in resp_data])
        self.statistic_info["memory_cost"] = max([x["memory"] for x in resp_data])
        # sum up the score in OI mode
        if self.problem.mode == PROBLEM_MODE.OI:
            score = 0
            try:
                for i in range(len(resp_data)):
                    if resp_data[i]["result"] == JudgeStatus.ACCEPTED:
                        resp_data[i]["score"] = self.problem.test_case_score[str(i)]
                        score += resp_data[i]["score"]
                    else:
                        resp_data[i]["score"] = 0
            except IndexError:
                logger.error(f"Index Error raised when summing up the score in problem {self.problem.id}")
                self.statistic_info["score"] = 0
                return
            self.statistic_info["score"] = score

    def judge(self):
        language = self.submission.language
        code = self.submission.code_source
        problem = self.sess.query(ProblemInfo).filter_by(id=self.problem_id).first()
        judge_params = {
            'src': code,
            'max_memory': problem.memory_limit * 1024 * 1024,
            'test_case_id': problem.test_id,
            'max_cpu_time': problem.time_limit
        }
        with ChooseJudgeServer() as server:
            # if not server:
            #     print('No Server')
            #     data = {"submission_id": self.submission.id, "problem_id": self.problem_id}
            #     submission_cache.push(json.dumps(data))
            #     return
            self.submission.result = JudgeStatus.JUDGING
            self.sess.commit()
            resp = self._request(urljoin(JUDGER_SERVER, "/judge"), data=judge_params, language=language)
        if not resp:
            self.submission.result = JudgeStatus.SYSTEM_ERROR
            self.sess.commit()
            return

        if resp["err"]:
            self.submission.result = JudgeStatus.COMPILE_ERROR
            self.statistic_info["err_info"] = resp["data"]
            self.statistic_info["score"] = 0
            self.submission.info = resp
        else:
            resp["data"].sort(key=lambda x: int(x["test_case"]))
            self.submission.info = resp
            self._compute_statistic_info(resp["data"])
            error_test_case = list(filter(lambda case: case["result"] != 0, resp["data"]))
            if not error_test_case:
                self.submission.result = JudgeStatus.ACCEPTED
            elif problem.mode == PROBLEM_MODE.ACM or len(error_test_case) == len(resp["data"]):
                self.submission.result = error_test_case[0]["result"]
            else:
                self.submission.result = JudgeStatus.PARTIALLY_ACCEPTED
        self.sess.commit()
        ups = self.sess.query(UserProblemStatus).filter_by(
            user_id=self.submission.user_id,
            problem_id=self.problem_id
        ).first()
        problem.submission_count = self.problem.submission_count + 1
        if not ups:
            ups = UserProblemStatus(
                user_id=self.submission.user_id,
                problem_id=self.problem_id,
            )
            exist = False
        else:
            exist = True
        if exist and ups.is_ac:
            return
        if self.problem.mode == PROBLEM_MODE.OI:
            now_score = self.statistic_info['score']
            is_ac = self.problem.total_score == now_score
            ups.is_ac = is_ac
            if is_ac:
                ups.ac_id = self.submission.id
            ups.score = now_score
        else:
            is_ac = self.submission.result == JudgeStatus.ACCEPTED
            if is_ac:
                ups.ac_id = self.submission.id
            ups.is_ac = is_ac
        if not exist:
            self.sess.add(ups)
        self.sess.commit()

        if self.contest_id:
            self.update_contest_problem_status()

        self.sess.expire_all()
        self.sess.close_all()
        self.sess.close()

    def update_contest_problem_status(self):
        if self.contest.rule == ContestRuleType.ACM:
            self._update_acm_contest_rank()

        elif self.contest.rule == ContestRuleType.OI:
            self._update_oi_contest_rank()
        problem = self.sess.query(ProblemInfo).filter_by(id=self.problem.id).first()
        result = str(self.submission.result)
        problem_info = problem.statistic_info
        problem_info[result] = problem_info.get(result, 0) + 1
        submission_count = problem.submission_count
        if not submission_count:
            submission_count = 0
        ac_count = problem.ac_count
        if not ac_count:
            ac_count = 0
        wa_count = problem.wa_count
        if not wa_count:
            wa_count = 0
        if self.submission.result == JudgeStatus.ACCEPTED:
            ac_count = ac_count + 1
        else:
            wa_count = wa_count + 1
        self.sess.query(ProblemInfo).filter_by(id=self.problem.id).update({
            ProblemInfo.ac_count: ac_count,
            ProblemInfo.wa_count: wa_count,
            ProblemInfo.submission_count: submission_count,
            ProblemInfo.statistic_info: problem_info
        })
        self.sess.commit()

    def _update_acm_contest_rank(self):
        with Session(engine) as session:
            session.begin()
            rank = session.query(ACMRank).filter_by(cp_id=self.cp_id)
            user_rank = rank.filter_by(user_id=self.submission.user_id).first()
            ac_rank = rank.filter_by(is_ac=True).all()
            if not user_rank:
                is_ac = self.submission.result == 0
                submission_number = 1
                if is_ac:
                    diff_time = datetime.datetime.now() - self.contest.start_at
                    ac_time = diff_time.days * 24 * 3600 + diff_time.seconds
                    total_time = ac_time
                else:
                    ac_time = None
                    total_time = 20 * 60
                is_first_ac = len(ac_rank) == 0
                new_rank = ACMRank(
                    user_id=self.submission.user_id,
                    cp_id=self.cp_id,
                    submission_id=self.submission.id,
                    submission_number=submission_number,
                    total_time=total_time,
                    is_ac=is_ac,
                    is_first_ac=is_first_ac,
                    ac_time=ac_time
                )
                session.add(new_rank)
            else:
                if user_rank.is_ac:
                    return
                submission_number = user_rank.submission_number
                user_rank.submission_number = submission_number + 1
                is_ac = self.submission.result == 0
                if is_ac:
                    diff_time = datetime.datetime.now() - self.contest.start_at
                    ac_time = diff_time.days * 24 * 3600 + diff_time.seconds
                    total_time = submission_number * 20 * 60 + ac_time
                else:
                    ac_time = None
                    total_time = user_rank.total_time + 20 * 60
                is_first_ac = len(ac_rank) == 0 and is_ac
                user_rank.is_ac = is_ac
                user_rank.total_time = total_time
                user_rank.is_first_ac = is_first_ac
                user_rank.ac_time = ac_time
            session.commit()

    def _update_oi_contest_rank(self):
        with Session(engine) as session:
            session.begin()
            rank = session.query(OIRank).filter_by(
                user_id=self.submission.user_id,
                cp_id=self.cp_id,
            ).first()
            if not rank:
                rank = OIRank(
                    user_id=self.submission.user_id,
                    cp_id=self.cp_id,
                    submission_id=self.submission_id,
                    total_score=self.submission.statistic_info["score"],
                    submission_number=1,
                )
                is_ac = rank.total_score == self.problem.total_score
                rank.is_ac = is_ac
                if is_ac:
                    rank.ac_time = (datetime.datetime.now() - self.contest.start_at).seconds
                session.add(rank)
            else:
                last_score = rank.total_score
                if self.submission.statistic_info["score"] > last_score:
                    last_score = self.submission.statistic_info["score"]
                rank.total_score = last_score
                is_ac = rank.total_score == self.problem.total_score
                rank.is_ac = is_ac
                if is_ac:
                    rank.ac_time = (datetime.datetime.now() - self.contest.start_at).seconds
            session.commit()
