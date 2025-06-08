from fastapi import APIRouter
from Dependencies import scraping
from fastapi.responses import JSONResponse

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