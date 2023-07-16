import os
import importlib
import uvicorn
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination.utils import FastAPIPaginationWarning

import warnings


class OJBe(object):
    available = True

    def __init__(self, config_path) -> None:
        super().__init__()
        self.config = {}
        self.config_path = config_path
        self.check_config_is_available()
        self.load_config()
        self.host = self.config['server']['host']
        self.port = self.config['server']['port']
        self.app = FastAPI()

        self.setup()

    def setup(self):
        users_mw = importlib.import_module('OJ.middleware.users')
        urls = importlib.import_module('OJ.views')
        self.add_middleware(users_mw.CheckLogin)
        self.add_routes(urls.routes)
        db = importlib.import_module('OJ.db.database')
        db.Base.metadata.create_all(db.engine)

        if self.config['server'].get('is_cors', 0) == 1:
            self.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def check_config_is_available(self):
        try:
            self.config = yaml.load(open(self.config_path), yaml.Loader)
        except:
            assert False, 'Invalid config file.'
        self.config['server'] = self.config.get('server', {'host': '0.0.0.0', 'port': 16808})
        self.config['AES_KEY'] = self.config.get('AES_KEY', 'zjuerzclu')
        self.config['test_case'] = self.config.get('test_case', {'dir': './testcases'})

        assert (
                self.config.get('mysql', None) and
                self.config['mysql'].get('user', None) and
                self.config['mysql'].get('host', None) and
                self.config['mysql'].get('pass', None) and
                self.config['mysql'].get('port', None) and
                self.config['mysql'].get('name', None)
        ), 'Invalid MySQL config.'
        assert (
                self.config.get('redis', None) and
                self.config['redis'].get('host', None) and
                self.config['redis'].get('pass', None) and
                self.config['redis'].get('port', None) and
                self.config['redis'].get('db', None)
        ), 'Invalid Redis config.'

    def load_config(self):
        #  Server config
        os.environ['HOST'] = self.config['server']['host']
        os.environ['PORT'] = str(self.config['server']['port'])

        #  MySQL config
        os.environ['DB_USER'] = self.config['mysql']['user']
        os.environ['DB_PASS'] = self.config['mysql']['pass']
        os.environ['DB_HOST'] = self.config['mysql']['host']
        os.environ['DB_PORT'] = self.config['mysql']['port']
        os.environ['DB_NAME'] = self.config['mysql']['name']
        #  Redis config
        os.environ['REDIS_HOST'] = self.config['redis']['host']
        os.environ['REDIS_PORT'] = self.config['redis']['port']
        os.environ['REDIS_PASSWORD'] = self.config['redis']['pass']
        os.environ['REDIS_DB'] = self.config['redis']['db']
        #  AES Key
        os.environ['AES_KEY'] = self.config['AES_KEY']
        #  Judge server token
        os.environ['JUDGER_TOKEN'] = self.config['JUDGER_TOKEN']

    def add_route(self, route):
        self.app.include_router(route)

    def add_routes(self, routes):
        for route in routes:
            self.add_route(route)

    def add_middleware(self, mw, **kwargs):
        self.app.add_middleware(mw, **kwargs)

    def exclude_check_login(self, path):
        settings.CHECKLOGIN_EXCLUDE_PATH.append(path)

    def start(self):
        uvicorn.run(self.app, host=self.host, port=self.port)


warnings.simplefilter("ignore", FastAPIPaginationWarning)
