from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from db.session import engine , Base
import asyncio



async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


