from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
from .db import 

route = APIRouter()



# TODO: errors not handled
@route.get('/product', summary="scrap basic details from produc page")
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


@route.post('/store', summary="store product details in database")
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