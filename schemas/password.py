from pydantic import BaseModel , EmailStr
from datetime import datetime

class Changepasswordrequest(BaseModel):

    email : EmailStr

class ResetToken(BaseModel):

    email : EmailStr
    purpose : str
    jti : str
    exp : datetime

