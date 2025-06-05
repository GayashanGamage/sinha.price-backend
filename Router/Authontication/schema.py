from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    email : EmailStr
    password : str
    firstName : str
    createdAt : Optional[datetime] = Field(default_factory=datetime.now)
    emailNotification : Optional[bool] = Field(default=True)

class UserOnlyCredintials(BaseModel):
    email : EmailStr
    password : str
    
class emailVerification(BaseModel):
    email : EmailStr
    time : Optional[datetime] = Field(default_factory=datetime.now)