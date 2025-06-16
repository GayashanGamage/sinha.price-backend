from Dependencies.database import DB
from bson import ObjectId

database = DB()

def userDetails(email):
    """
    perpose : find user details using email
    response : userData - find successfully | Flase - no user under provided email
    """
    data = database.users.find_one({'email' : email}, {'password' : 0})
    if data == None:
        return False
    elif data != None:
        return data
    
def setNotificationOnTracks(id):
    """
    perpose : freeze notification for all tracking products
    response : True - successfull | False - cannot update 'tracking' table correctly
    """
    data = database.tracking.update_many({'userId' : id}, {'$set' : {'emailNotification' : True}})
    print(data)
    if data.acknowledged == True:
        return True
    elif data.acknowledged == False:
        return False
    
def setNotificationOnTrack(trakingid, trackingStatus):
    """
    perpose : freeze notification for single tracking product
    response : True - successfull | False - cannot update 'tracking' table correctly
    """
    # print(f'traking ID {trakingid}, tracking status {trackingStatus}')
    data = database.tracking.update_one({'_id' : ObjectId(trakingid)}, {'$set' : {'emailNotification' : trackingStatus}})
    print(data)
    if data.matched_count == 1:
        return True
    elif data.matched_count == 0:
        return False
    
def userUpdate(id):
    """
    perpose :
    response :
    """
    print(f'this is user id {id}')
    data = database.users.update_one({'_id' : id}, {'$set' : {'emailNotification' : True}})
    if data.acknowledged == True:
        return True
    elif data.acknowledged == False:
        return False