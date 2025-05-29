from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from Schemas import productDetails, trackData
from fastapi.middleware.cors import CORSMiddleware
from user import auth, authVerification
from typing import Dict
from pprint import pprint
from bson import ObjectId
import schedule

# mondoDB database config 
load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
cluster = mongo['price_platform']
product = cluster['product']
users = cluster['user']
tracks = cluster['tracks']
email = cluster['email']

app = FastAPI()
app.include_router(auth)

# middleware config
origins = [
    "https://sigiriprice.gamage.dev",
    "http://sigiriprice.gamage.dev",
    "sigiriprice.gamage.dev",
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
    # get user details form User table
    userInfo = users.find_one({'email' : data['email']})
    # print(userInfo)
    # check validity of JWT token
    if data == False or userInfo == None:
        return JSONResponse(status_code=401, content={'error' : 'JWT token is not valid'})
    else:
        # find user details from product table
        productInfo = product.find_one({'link' : product_details.link})
        # if product not available add to database
        if productInfo == None:
            productInfo = product.insert_one(product_details.dict())
            # check tracks regard to user
            tracksInfor = tracks.find_one({'user_id' : data['id']})
            if tracksInfor == None:
                # create new tracks document in tracks table
                tracks.insert_one({'user_id' : data['id'], 'product' : [{'product_id' : productInfo.inserted_id, 'price' : product_details.track_price, 'send' : False, 'email_id' : None}]})
            else:
                tracks.update_one({'user_id' : data['id']}, {'$push' : { 'product' : {'product_id' : productInfo.inserted_id, 'price' : product_details.track_price, 'send' : False, 'email_id' : None}}})
        else:
            # check tracks regard to user
            tracksInfor = tracks.find_one({'user_id' : data['id']})
            if tracksInfor == None:
                # create new tracks document in tracks table
                tracks.insert_one({'user_id' : data['id'], 'product' : [{'product_id' : productInfo['_id'], 'price' : product_details.track_price, 'send' : False, 'email_id' : None}]})
            else:
                tracks.update_one({'user_id' : data['id']}, {'$push' : { 'product' : {'product_id' : productInfo['_id'], 'price' : product_details.track_price, 'send' : False, 'email_id' : None}}})
        return JSONResponse(status_code=200, content={'messsage' : 'successfull'})
    

@app.delete('/remove-product/{item_id}', summary='this is for remove single product from track list')
async def removeProduct(item_id:str,  data = Depends(authVerification)):
    trackProduct = tracks.update_one({'user_id' : data['id']}, {'$pull' : {'product' :{ 'product_id': ObjectId(item_id)}}})
    if trackProduct.modified_count == 0:
        return JSONResponse(status_code=400, content={'error' : 'content not available'})
    else:
        return JSONResponse(status_code=200, content={'message' : 'successful'})

@app.get('/get-products', summary='get all product tracks by user')
async def getProducts(data = Depends(authVerification)):
    # token validation 
    if data == False:
        return JSONResponse(status_code=401, content={'error' : 'unauthorized request'})
    else:
        # aggregate pipelines 
        pipline1 = {'$match' : {'user_id' : data['id']}}
        pipline2 = {'$unwind' : '$product'}
        pipline3 = {'$lookup' : {'from' : 'product', 'localField' : 'product.product_id', 'foreignField' : '_id', 'as' : 'products'}}
        pipline4 = {'$unset' : ['user_id', '_id', 'product.email_id', 'products._id']}
        # combine tracks and product table
        tracksProducts = tracks.aggregate([pipline1, pipline2, pipline3, pipline4])
        # manual type conversion 
        trackProductsList = []
        for item in tracksProducts:
            item['product']['product_id'] = str(item['product']['product_id'])
            trackProductsList.append(item)
        # output
        return JSONResponse(content=trackProductsList)

@app.put('/track-update', summary='update track product price')
async def trackUpdate(track_id : str, price : int, data = Depends(authVerification)):
    tracksInformation = tracks.update_one({'user_id' : data['id'], 'product.product_id' : ObjectId(track_id)}, {'$set' : {'product.$.price' : price}})
    if tracksInformation.modified_count > 0:
        return JSONResponse(status_code=200, content='successful')
    else:
        return JSONResponse(status_code=404, content='update cannot be done')


