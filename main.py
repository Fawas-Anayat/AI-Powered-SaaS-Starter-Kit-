from api.v1.endpoints import crud , files
from fastapi import FastAPI
from fastapi import APIRouter
import models

app = FastAPI()

app.include_router(crud.router,prefix="")
app.include_router(files.router, prefix="")


