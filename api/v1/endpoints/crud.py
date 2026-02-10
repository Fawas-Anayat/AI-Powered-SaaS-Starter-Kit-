from fastapi import APIRouter , Depends , HTTPException , status , Response
from db.session import Base
from ..dependencies import get_async_db , authenticate_user
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserSignup
from models.models import User , UserSession , Refresh_Token 
from core.security import hash_password , verify_password , create_tokens , get_token_hash , create_access_token , create_refresh_token
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from ..redis_utils import save_refresh_token_redis , verify_refresh_token_redis , delete_refresh_token_redis



router = APIRouter()


# for the signup we can also implement the recapthca , rate limiting and for the proper error handling can use the try catch block , can track the failed attempts for the security reasons and the terms and conditions check
# can also add the "continue with google" etc

@router.post("/signup")
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

@router.post("/login")
async def login(response : Response ,form_data :  OAuth2PasswordRequestForm = Depends() , db : AsyncSession = Depends(get_async_db)) :
    auth_user = await authenticate_user(form_data.username, form_data.password ,db)

    if auth_user is not False:
        user={
            "user_id" : auth_user.user_id,
            "email" : auth_user.email ,
            "name" : auth_user.username
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password"
        )
    
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    # saving the refresh token in the redis
    await save_refresh_token_redis(
        user_id=auth_user.user_id,refresh_token=refresh_token
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=1800,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=604800,
        path="/"
    )

    await db.commit()

    return {
        "message": "User logged in successfully",
        "user": {
            "user_id": auth_user.user_id,
            "username": auth_user.username,
        }
    }













# email+password --> verify password 
# check the user in the database if not present raise httpexception else 
# make a refresh token and the access token and create a session
# save the refresh token metadata in the db and save refresh token hashed in redis and return to user both the access and the refresh token in the httponly cookies
        

    


