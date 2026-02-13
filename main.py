from api.v1.endpoints import crud , files , chat
from fastapi import FastAPI
from fastapi import APIRouter
import models
from core.logging_config import LOGGING_CONFIG
from logging.config import dictConfig
import logging

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(crud.router,prefix="")
app.include_router(files.router, prefix="")
app.include_router(chat.router)


