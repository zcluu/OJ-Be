import typing

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.orm import Session

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, DispatchFunction
from starlette.types import ASGIApp

from OJ.db.database import engine
from OJ.models.UserModels import UserSession

from OJ.app.settings import CHECKLOGIN_EXCLUDE_PATH


class CheckLogin(BaseHTTPMiddleware):

    def __init__(self, app: ASGIApp, dispatch: typing.Optional[DispatchFunction] = None) -> None:
        super().__init__(app, dispatch)
        self.app = app

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path: str = request.get('path')
        for it in CHECKLOGIN_EXCLUDE_PATH:
            if path.startswith(it):
                response = await call_next(request)
                return response
        else:
            with Session(engine) as session:
                session.begin()
                token = request.headers.get('token', '')
                sess = session.query(UserSession).filter(UserSession.token == token).first()
                if not sess:
                    print('not login')
                    return JSONResponse({}, status_code=status.HTTP_401_UNAUTHORIZED)
                response = await call_next(request)
                session.close()
            return response
