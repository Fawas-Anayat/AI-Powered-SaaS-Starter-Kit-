from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from db.session import engine , Base
import asyncio


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())