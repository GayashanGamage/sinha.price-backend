from fastapi import APIRouter
from Dependencies import scraping, JWTtoken
from fastapi.responses import JSONResponse
from . import schema
from . import db
from fastapi import Depends

productRoute = APIRouter(prefix='/product')

"""
How to add new store to existing code base
1. add all infomation (store, functionName and url) in to the stores variable
2. add scrapping function in to the 'scraping.py' file.
3. function name should be same to the function name of the 'scraping.py' file
"""
stores = [
    {
        'store' : 'sinhagiri',
        'functionName' : 'SinhagiriScrapper',
        'url' : 'https://singhagiri.lk',
    }
]




@productRoute.get('/', tags=['product'])
async def getProductDetails(url : str,):
    # validate the store url
    for item in stores:
        if item['url'] == url[0:len(item['url'])]:
            # build url
            storeFunction = getattr(scraping, item['functionName'])
            # validate the product
            product =  storeFunction(url)
            if product == False:
                return JSONResponse(status_code=404, content={'messege' : 'scrape not successfull'})
            else:
                return JSONResponse(status_code=200, content={'messege' : 'successfull', 'prodcut' : product, 'store' : item['store']})
        else:
            return JSONResponse(status_code=400, content={'messege' : 'untrackable site'})
        
@productRoute.post('/track', tags=['product'])
async def trackProduct(productData : schema.TrackingProductDetails, credencials=Depends(JWTtoken.authVerification)):
    # evaluate credencials
    if credencials != False:

        # check duplicate product in 'Product' table
        userId = db.getUserId(credencials['email'])
        product = db.checkProductAvailability(productData.product.productLink)
        
        # product is not duplicated
        if product ==  False:
            
            # insert as a new product
            storeProductData = db.setProduct(productData.product)
            print('store product')
            newTrackingData = productData.tracking.model_dump(mode='json')
            
            # allocating new fields to "Trackign" product
            newTrackingData['userId'] = userId
            newTrackingData['productId'] = storeProductData

            # store 'Tracking' data
            tracks = db.setTracking(newTrackingData)
        
        # product found on 'Product' table
        elif product != False:
            
            # check tracking duplication related to user email 
            duplicateTracking = db.trackingDuplication(product, userId)
            
            # not tracking duplication found
            if duplicateTracking == False:
                newTrackingData = productData.tracking.model_dump(mode='json')
                
                # allocating new fields to "Trackign" product
                newTrackingData['userId'] = userId
                newTrackingData['productId'] = product
                tracks = db.setTracking(newTrackingData)
            
            # 'Tracking' dupliate found
            elif duplicateTracking != False:
                return JSONResponse(status_code=400, content={"message" : "duplication product found"})
        
        # all data store successfull
        if tracks != False:
            return JSONResponse(status_code=200, content={'message' : 'successfull'})
        
        # something go wrong in server
        elif tracks == False:
            return JSONResponse(status_code=500, content={'message' : 'try again letter'})
    
    # unauthorized access
    elif credencials == False:
        return JSONResponse(status_code=404, content={'message' : 'unauthorized access'})

@productRoute.get('/summery', tags=['product'])
async def trackSummery(credencials = Depends(JWTtoken.authVerification)):
    if credencials != False:
        
        # get user Id
        userData = db.getUserId(credencials['email'])
        if userData != False:
            
            # request summerize tracking products
            productData = db.trackProductSummery(userData)
            if len(productData) == 0:
                return JSONResponse(status_code=200, content={'message' : 'empty trckings', 'data' : []})
            elif len(productData) >= 1:

                # serialize data output
                for item in productData:
                    item['_id'] = str(item['_id'])

                return JSONResponse(status_code=200, content={'message' : 'successfull', 'data' : productData})
        
        # unavailable user data under provided email 
        elif userData == False:
            return JSONResponse(status_code=400, content={'message' : 'invalied email address'})
    
    # unauthorized access 
    elif credencials == False:
        return JSONResponse(status_code=404, content={'message' : 'unauthorized access'})
    

@productRoute.patch('/updateprice', tags=['product'])
async def updatePrice(productdata : schema.priceUpdate, credencials = Depends(JWTtoken.authVerification)):
    # check authontication is validate or not
    if credencials == False:
        return JSONResponse(status_code=404, content={'message' : 'unauthonticated user'})
    else:
        # find and update document
        update = db.udpateTrackingPrice(productdata.id, productdata.priceUpdateWithoutId())
        # return rsponce
        if update == True:
            return JSONResponse(status_code=200, content={'message' : 'update sucessful'})
        elif update == False:
            return JSONResponse(status_code=500, content={'message' : 'update not sucsessful'})
    
@productRoute.delete('/delete', tags=['product'])
async def deleteProduct(id : str, credencials = Depends(JWTtoken.authVerification)):
    # authonticating request
    # delete tracking
    # responce
    if credencials != False:
        data = db.removeTracking(id)
        if data == False:
            return JSONResponse(status_code=400, content={'message' : 'tracking not found'})
        elif data != False:
            return JSONResponse(status_code=200, content={"message" : 'successfull'})
    elif credencials == False:
        return JSONResponse(status_code=404, content={'message' : 'unauthorized'})