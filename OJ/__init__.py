import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination.utils import FastAPIPaginationWarning

from .app.settings import HOST, PORT
from .db.database import Base, engine
from .views import *
from .models import *
from .middleware import users
import warnings

from .views.admin import *


class OJBe(object):

    def __init__(self, host=HOST, port=PORT, cors=True) -> None:
        super().__init__()
        self.host = host
        self.port = port

        self.app = FastAPI()

        if cors:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.add_routes([
            problems_router,
            user_router,
            sub_router,
            con_router,
            admin_problem_router,
            admin_sys_router,
            admin_contest_router
        ])

    def add_route(self, route):
        self.app.include_router(route)

    def add_routes(self, routes):
        for route in routes:
            self.add_route(route)

    def add_middleware(self, mw, **kwargs):
        self.app.add_middleware(mw, **kwargs)

    def start(self):
        uvicorn.run(self.app, host=self.host, port=self.port)


warnings.simplefilter("ignore", FastAPIPaginationWarning)
