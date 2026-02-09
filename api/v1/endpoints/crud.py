from fastapi import APIRouter , Depends , HTTPException , status
from db.session import Base
from ..dependencies import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserSignup
from models.models import User , UserSession , Refresh_Token 
from core.security import hash_password , verify_password
from sqlalchemy import select


router = APIRouter()


# for the signup we can also implement the recapthca , rate limiting and for the proper error handling can use the try catch block , can track the failed attempts for the security reasons and the terms and conditions check
# can also add the "continue with google" etc

@router.post("")
async def signup_user(user_signup : UserSignup , db : AsyncSession = Depends(get_async_db)):
    try:

        result =await db.execute(select(User).where(User.email == user_signup.email))
        user_email = result.one_or_none()


        if  user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST , detail="user with this email already exist"
            )
        
        result = await db.execute(select(User).where(User.username == user_signup.username))
        user_name = result.scalar_one_or_none()

        if user_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST , detail="username already taken"
            )
        
        hashed_password = hash_password(user_signup.password)

        new_user = User(
            username = user_signup.username ,
            email = user_signup.email ,
            hashed_password = hashed_password

        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {
            "message" : "user created successfully" , "user_id" : new_user.user_id
        }
    
    except HTTPException:

        raise
    except HTTPException as e :
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during user registration"
        )

        

    


