from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class productDetails(BaseModel):
    link : str
    price : int
    title : str
    availability : bool
    viewable : bool

class Credentials(BaseModel):
    email : EmailStr
    password : str

class User(Credentials):
    first_name : str
    created : datetime =Field(default=datetime.now())