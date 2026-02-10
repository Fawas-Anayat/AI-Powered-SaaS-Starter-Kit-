from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from db.session import engine , Base
from models.models import User
from sqlalchemy import select
from core.security import verify_password , hash_password



async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

async def authenticate_user(email : str , password : str , db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return False
    
    if not verify_password(plain_password=password,hashed_password=hash_password(password)):
        return False
    
    return user


