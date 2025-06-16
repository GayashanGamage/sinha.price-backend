from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime
from typing import Optional
from bson import ObjectId

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
    lastUpdate : Optional[datetime] = Field(default_factory=datetime.now)
    emailNotification : Optional[bool] = Field(default=True)

class TrackingProductDetails(BaseModel):
    product : Product
    tracking : Tracking

class priceUpdate(BaseModel):
    id : str
    myPrice : int
    lastUpdate : Optional[datetime] = Field(default_factory=datetime.now)
    
    @field_validator("id")
    def validate_id(cls, value):
        return ObjectId(value)

    def priceUpdateWithoutId(self):
        return {
            "myPrice" : self.myPrice,
            "lastUpdate" : self.lastUpdate
        }