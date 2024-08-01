from fastapi import FastAPI
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from Schemas import productDetails
from fastapi.middleware.cors import CORSMiddleware
from user import auth

# mondoDB database config 
load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
cluster = mongo['price_platform']
items = cluster['items']

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
async def storeProduct(product_details : productDetails):
    """
    this is for store / update 'track by' filed for product
    """
    getItem = items.find_one({'link' : product_details.link[30:]})
    if getItem == None:
        items.insert_one({'link' : product_details.link[30:], 'created' : datetime.now(), 'track_count' : 1, 'current_price' : product_details.price, 'title' : product_details.title, 'availability' : product_details.availability, 'viewable' : product_details.viewable})
    else:
        items.update_one({'link' : product_details.link[30:]}, { '$inc' : {'track_count' : 1}})
    return JSONResponse(status_code=201, content={'message' : 'successful'})

@app.get('/test')
def test():
    return JSONResponse(status_code=200, content={'message' : 'success'})