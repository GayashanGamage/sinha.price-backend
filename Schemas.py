from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class productDetails(BaseModel):
    link : str
    price : str
    track_price : int
    title : str
    code : str  
    availability : str

class Credentials(BaseModel):
    email : EmailStr
    password : str

class User(Credentials):
    first_name : str
    created : datetime =Field(default=datetime.now())

# output details ----------------------------