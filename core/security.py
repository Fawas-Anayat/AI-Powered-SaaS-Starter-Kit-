from passlib.context import CryptContext
from datetime import datetime , timedelta , timezone
from typing import Optional
from core.config import settings
import uuid
from jose import jwt , JWTError
from fastapi import HTTPException , status
import secrets
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)




def create_access_token(data : dict,expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60)

    jti_id = str(uuid.uuid4())

    iat_ts = int(datetime.utcnow().timestamp())
    exp_ts = int(expire.timestamp())
    to_encode.update({"jti": jti_id})
    to_encode.update({
        "iat": iat_ts,
        "exp": exp_ts,
        "user_id": data["user_id"],
        "email": data["email"],
        "name": data.get("name"),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY , algorithm=settings.ALGORITHM)
    return encoded_jwt




def create_refresh_token(data : dict ):
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    iat_ts = int(now.timestamp())
    exp_ts = int(expire.timestamp())

    payload = {
        "sub": data["name"],
        "iat": iat_ts,
        "exp": exp_ts,
        "user_id": data["user_id"],
        "type": "refresh",
        "jti": str(uuid.uuid4())
    }

    encoded_ref_token = jwt.encode(payload, settings.SECRET_KEY,algorithm=settings.ALGORITHM)

    return encoded_ref_token


def create_tokens(user: dict) -> dict:

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def get_token_hash(token : str):
    return pwd_context.hash(token)



def verify_token(token : str):
    payload = jwt.decode(token , settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED , detail="invalid token"
        )
    
    return user_id


from datetime import datetime, timedelta, timezone
import uuid
from jose import jwt

def generate_reset_token(email: str):
    jti = str(uuid.uuid4())  

    data = {
        "sub": email,
        "purpose": "password_reset",
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10)
    }

    token = jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token, jti


    

# notes --browsers send the cookies with each request to the same domain from where they came ,,