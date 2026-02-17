from api.v1.endpoints import crud , files , chat
from fastapi import FastAPI
from fastapi import APIRouter
from core.logging_config import LOGGING_CONFIG
from logging.config import dictConfig
import logging
from api.v1.helper_functions import create_tables
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()  
    yield

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(crud.router,prefix="")
app.include_router(files.router, prefix="")
app.include_router(chat.router,prefix="")


