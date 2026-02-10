from api.v1.endpoints import auth , crud
from fastapi import FastAPI
from fastapi import APIRouter
import models

app = FastAPI()

app.include_router(crud.router,prefix="")


