from Dependencies.database import DB

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
    
def trackingDuplication(id, email):
    """
    perpose : find duplicate products related to same user
    response : True - duplicated product tracking | False - unique tracking 
    """
    data = database.tracking.find_one({'email' : email, 'id' : id})
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