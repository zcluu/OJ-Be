from .problems import router as problems_router
from .user import router as user_router
from .submission import router as sub_router
from .contests import router as con_router
from .admin import *

routes = [
    problems_router,
    user_router,
    sub_router,
    con_router,
    admin_problem_router,
    admin_sys_router,
    admin_contest_router
]
