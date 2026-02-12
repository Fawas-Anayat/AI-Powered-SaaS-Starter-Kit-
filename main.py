from api.v1.endpoints import crud , files , chat
from fastapi import FastAPI
from fastapi import APIRouter
import models

app = FastAPI()

app.include_router(crud.router,prefix="")
app.include_router(files.router, prefix="")
app.include_router(chat.router)


