from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    productLink : HttpUrl
    price : str
    title : str
    code : str
    availability : bool
    img : HttpUrl
    addedDate : Optional[datetime] = Field(default_factory=datetime.now)
    lastUpdate : Optional[datetime] = Field(default_factory=datetime.now)

class Tracking(BaseModel):
    defaultPrice : str
    myPrice : int
    stertedDate : Optional[datetime] = Field(default_factory=datetime.now)    

class TrackingProductDetails(BaseModel):
    product : Product
    tracking : Tracking