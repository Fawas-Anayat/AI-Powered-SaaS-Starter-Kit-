from pydantic import BaseModel , EmailStr , Field , field_validator
import re

class UserSignup(BaseModel):

    username : str = Field(...,max_length=20 , min_length=5)
    email : EmailStr = Field(...)
    password : str = Field(...,max_length=16 , min_length=5 )

    @field_validator('password')
    def validate_password(cls , v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain a number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        
        return v
    
    @field_validator('username')
    def validate_name(cls , v):

        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscore')
        
        if v[0].isdigit():
            raise ValueError('Username cannot start with a number')
        
        reserved = ['admin', 'root', 'system', 'user', 'test']

        if v.lower() in reserved:
            raise ValueError('This username is reserved')
        
        return v.lower()
    
    





