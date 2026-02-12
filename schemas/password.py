from pydantic import BaseModel , EmailStr
from datetime import datetime

class Changepasswordrequest(BaseModel):

    email : EmailStr

class ResetPasswordRequest(BaseModel):

    token : str
    new_password : str
