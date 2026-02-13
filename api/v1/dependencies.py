from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from db.session import engine , Base
from models.models import User
from sqlalchemy import select 
from core.security import verify_password , hash_password
from fastapi import Cookie , Depends , HTTPException , status
from core.security import verify_token



async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

async def authenticate_user(email : str , password : str , db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return False
    
    if not verify_password(plain_password=password,hashed_password=user.hashed_password):
        return False
    
    return user

#in fastapi a non default value can't come after the default value
async def get_current_user(db : AsyncSession = Depends(get_async_db), access_token : str = Cookie(default=None)) -> bool:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED , detail="access token missing"
        )
    
    user_id = verify_token(access_token)

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED , detail="no user found"
        )
    
    return user

