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
            duplicateTracking = db.trackingDuplication(product, credencials['email'])
            
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