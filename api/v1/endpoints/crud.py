from fastapi import APIRouter , Depends , HTTPException , status , Response , Cookie
from db.session import Base
from ..dependencies import get_async_db , authenticate_user ,get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserSignup
from models.models import User , UserSession , Refresh_Token 
from core.security import hash_password , verify_password , create_tokens , get_token_hash , create_access_token , create_refresh_token , verify_token , generate_reset_token
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from ..redis_utils import save_refresh_token_redis , verify_refresh_token_redis , delete_refresh_token_redis , redis_client
from jose import jwt , JWTError
from core.config import settings
from schemas.password import Changepasswordrequest , ResetPasswordRequest
import redis
from services.email_service import send_password_reset_email



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

# the logic of the refresh end point is as follow -> whent the user hits the refresh end point the server gets the refresh token from the cookies and then first checks if there is refresh token available or not ,,if yes the it checks whether its correct and if yes then it checks whether the user of this token is present in the db and if yes then it creates the new refresh as well as the access token and deletes the old ones and sets back the cookies with the new tokens and saves the hashed new refresh token in the db



@router.get("/refresh")
async def refresh(response : Response , refresh_token : str = Cookie(default=None) , db : AsyncSession = Depends(get_async_db)):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token missing"
        )
    
    user_id = verify_token(token=refresh_token)

    is_valid = await verify_refresh_token_redis(user_id=user_id, refresh_token=refresh_token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or already used"
        )
    
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists"
        )
    
    user_data = {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.username,
    }

    await delete_refresh_token_redis(user_id=user_id)

    new_access_token = create_access_token(user_data)
    new_refresh_token = create_refresh_token(user_data)

    await save_refresh_token_redis(user_id=user_id, refresh_token=new_refresh_token)

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=1800,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=604800,
        path="/"
    )

    return {"message": "Tokens refreshed successfully"}




@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str = Cookie(default=None),
    access_token: str = Cookie(default=None),
    db: AsyncSession = Depends(get_async_db)
):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing"
        )

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")
        token_type = payload.get("type")

        if not user_id or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    if refresh_token:
        await delete_refresh_token_redis(user_id=user_id)



    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")

    return {"message": "Logged out successfully"}



# store the reset token in the redis if we want better performance and store in the db if we want the  better control over the user working and we want to store the audit logs and track whats the user is doing,,,the second aproach is more used in the SaaS.

@router.post("/forgotPassword")
async def forgot_password(
    email: Changepasswordrequest,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(User).where(User.email == email.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If this user exists, then a reset email has been sent"}

    reset_token, jti = generate_reset_token(user.email)

    await redis_client.set(
        f"pwd_reset:{jti}",
        user.user_id,
        ex=600  
    )

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    await send_password_reset_email(user.email, reset_link)

    return {"message": "If this user exists, then a reset email has been sent"}





@router.post("/resetPassword")
async def reset_password(payload : ResetPasswordRequest , db:AsyncSession = Depends(get_async_db)):
    try:
        decoded = jwt.decode(payload.token, settings.SECRET_KEY , algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED , detail="invalid or expired token"
        )
    
    if decoded.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid token type")
    
    jti = decoded.get("jti")
    email = decoded.get("sub")

    user_id = await redis_client.get(f"pwd_reset:{jti}")

    if not user_id:
        raise HTTPException(status_code=400, detail="Token expired or already used")
    
    new_hashed_password = hash_password(payload.new_password)

    result = await db.execute(select(User).where(User.user_id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = new_hashed_password
    await db.commit()

    await redis_client.delete(f"pwd_reset:{jti}")

    return {"message": "Password has been reset successfully"}





    





    

    






#if I(browser) have a cookie for this domain, I attach it to every request going to that domain, regardless of where that request originated from.this is known as the CSRF and to prevent this we use the CSRF tokens that are explicitely sent to the front end and are sent to the server with each request

# the refresh tokens are stored in the redis only if we want speed ,,
# but if we want more security and the control we store the meta data of the refresh tokens in the db and track them but every time hitting the db









# notes
# email+password --> verify password 
# check the user in the database if not present raise httpexception else 
# make a refresh token and the access token and create a session
# save the refresh token metadata in the db and save refresh token hashed in redis and return to user both the access and the refresh token in the httponly cookies
        

    


