from Dependencies.database import DB
from bson import ObjectId

database = DB()

def checkProductAvailability(productLink):
    """
    perpose : find the product in database
    response : False : product not available | productId : product is available
    """
    productData = database.product.find_one({'productLink' : f'{productLink}'})
    if productData == None:
        return False
    else:
        return productData['_id']
    
def setProduct(data):
    """
    perpose : store product data and get ID
    response : productId : store data successfully | False : unsuccessfull data store transaction
    """
    print(data.model_dump(mode='json'))
    productInsert = database.product.insert_one(data.model_dump(mode='json'))
    print('inserted data')
    if productInsert.acknowledged == True:
        return productInsert.inserted_id
    else:
        return False
    
def setTracking(data):
    """
    perpose : store tracking data
    response : True : store successfull | False : unsuccessfull transaction
    """
    print(data)
    settracking = database.tracking.insert_one(data)
    if settracking.acknowledged == True:
        return True
    elif settracking.acknowledged == False:
        return False
    
def trackingDuplication(productId, userId):
    """
    perpose : find duplicate products related to same user
    response : True - duplicated product tracking | False - unique tracking 
    """
    data = database.tracking.find_one({'userId' : userId, 'productId' : productId})
    if data == None:
        print('tracking is not duplicated')
        return False
    elif data != None:
        print('tracking is duplicated')
        return True

def getUserId(email):
    """
    perpose : get user id
    response : userId - find userId succesfully | false - invalied email
    """
    userData = database.users.find_one({'email' : email})
    if userData != None:
        return userData['_id']
    elif userData == None:
        return False
    
def trackProductSummery(userId):
    """
    perpose : get all tracking product data as summerization
    responce : Dataset - if there any tracking products | False : no any products 
    """
    pipeline = [
        {
            '$match' : {
                'userId' : userId
            }
        },
        {
            '$lookup': {
                'from': "Product",  
                'localField': 'productId',  
                'foreignField': '_id',  
                'as': 'productInfo'  
            }
        },
        {
            '$unwind': '$productInfo' 
        },
        {
            '$project': {
                'defaultPrice': 1,  
                'myPrice': 1,       
                'title': '$productInfo.title',  
                'code' : '$productInfo.code'
            }
        }
    ]
    # Perform the aggregation
    result = database.tracking.aggregate(pipeline)
    trackList = []
    for item in result:
        trackList.append(item)

    if len(trackList) == 0:
        return False
    elif len(trackList) >= 1:
        return trackList    

def udpateTrackingPrice(id, updatedData):
    """
    perpose : udpate the myPrice in tracking product
    response : True - update successfuly | False - unsuccessful transaction
    """
    data = database.tracking.find_one_and_update({'_id' : id}, {'$set' : updatedData})
    if data == None:
        return False
    else:
        return True
















    

# generate a mongodb querry using pymongo for this senario

# product table

# '_id' : objectId(),
# 'productLink' : str,
# 'price' : int,
# 'title' : str,
# 'code' : str,
# 'availability' : bool,
# 'img' : str,
# 'addedDate' : datetime,
# 'lastUpdate' : datetime


# tracking table
# '_id' : objectId
# 'defaultPrice' : str,
# 'myPrice' : int,
# 'startedDate' : datetime
# 'userId' : objectId,
# 'productId' : objectId

# I want to joint traking table and product table base provide 'userId'. limit the output field from product table to produt 'title'. output should be print each column. 