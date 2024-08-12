from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from Schemas import productDetails
from fastapi.middleware.cors import CORSMiddleware
from user import auth, authVerification
from typing import Dict

# mondoDB database config 
load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
cluster = mongo['price_platform']
product = cluster['product']
users = cluster['user']
tracks = cluster['tracks']

app = FastAPI()
app.include_router(auth)

# middleware config
origins = [
    "https://sigiriprice.gamage.me",
    "http://sigiriprice.gamage.me",
    "sigiriprice.gamage.me",
    "http://localhost:5173",
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO: errors not handled
@app.get('/product', summary="scrap basic details from produc page")
async def getProduct(link : str):
    """
    this is for scrappe data from sinhagiri website - product page
    """
    b = requests.get(link).text
    a = BeautifulSoup(b, "html.parser")
    # product code
    c = list(a.select('.product-sku'))
    product_code = c[1].text[11:]
    # product title
    product_title = a.select_one('.product-title').text
    # availability
    availability = a.select_one('.bg-success').text
    # price 
    # d = list(a.select('.data'))
    # price = d[1].text

    try:
        b = list(a.select('.data'))
        price = b[1].text
    except:
        b = list(a.select('.selling-price'))
        price = b[0].text

    # image
    e = list(a.select_one('.product-slider__main-slider__item'))
    image = e[0].span.img['src']
    return JSONResponse(status_code=200, content={
        'title' : product_title,
        'availability' : availability,
        'code' : product_code,
        'price' : price,
        'image' : image
    })


@app.post('/store', summary="store product details in database")
async def storeProduct(product_details : productDetails, data = Depends(authVerification)):
    """
    this is for store / update 'track by' filed for product
    """
    # find user details 
    user_details = users.find_one({'email' : data.email})
    # find the product
    pdct_detail = product.find_one({'link' : product_details.link})
    # if product is not there add it to database
    if pdct_detail == None:
        insert_product = product.insert_one(product_details.dict())
    # if product is available
    else:
        pdct_detail['_id'] = str(pdct_detail['_id'])
         



    # return JSONResponse(status_code=200, content=pdct_detail)
    

@app.delete('/remove-product', summary='this is for remove single product from track list')
async def removeProduct():
    pass


