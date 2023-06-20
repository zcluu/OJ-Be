class PROBLEM_MODE:
    ACM = 0
    OI = 1


class PROBLEM_STATUS:
    VISIBLE = 0
    HIDDEN = 1
    CONTEST_HIDDEN = 2
    CONTEST_VISIBLE = 3


class ContestStatus:
    CONTEST_NOT_START = "1"
    CONTEST_ENDED = "-1"
    CONTEST_UNDERWAY = "0"


class ContestRuleType:
    ACM = 0
    OI = 1


class CONTEST_TYPE:
    NORMAL = 0
    PASSWORD = 1
    HIDDEN_VISIBLE = 2
    HIDDEN_INVISIBLE = 3


class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    JUDGING = 7
    PARTIALLY_ACCEPTED = 8


class CacheKey:
    waiting_queue = 'waiting_queue'
