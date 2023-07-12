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
        if request.method == 'OPTIONS':
            response = await call_next(request)
            return response
        path: str = request.get('path')
        for it in CHECKLOGIN_EXCLUDE_PATH:
            if path.startswith(it):
                response = await call_next(request)
                return response
        else:
            with Session(engine) as session:
                session.begin()
                token = request.headers.get('x-token', '')
                sess = session.query(UserSession).filter(UserSession.token == token).first()
                if not sess:
                    return JSONResponse({}, status_code=status.HTTP_401_UNAUTHORIZED)
                if path.startswith('/api/admin') and not sess.user.is_admin:
                    return Response('NOT ACCEPTABLE REQUEST', status_code=status.HTTP_406_NOT_ACCEPTABLE)
                response = await call_next(request)
                session.close()
            return response
