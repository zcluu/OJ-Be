from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination.utils import FastAPIPaginationWarning

from .db.database import Base, engine
from .views import *
from .models import *
from .middleware import users
import warnings

warnings.simplefilter("ignore", FastAPIPaginationWarning)

app = FastAPI()
Base.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(users.CheckLogin)

app.include_router(problems_router)
app.include_router(user_router)
app.include_router(sub_router)
app.include_router(con_router)
