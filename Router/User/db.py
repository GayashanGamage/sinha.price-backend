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
    
def setNotificationOnTracks(id, notificationStatus):
    """
    perpose : freeze notification for all tracking products
    response : True - successfull | False - cannot update 'tracking' table correctly
    """
    data = database.tracking.update_many({'userId' : ObjectId(id)}, {'$set' : {'allEmailNotification' : notificationStatus}})
    if data.acknowledged == True:
        return True
    elif data.acknowledged == False:
        return False
    
def setNotificationOnTrack(trakingid, trackingStatus, allTrackingStatus):
    """
    perpose : freeze notification for single tracking product
    response : True - successfull | False - cannot update 'tracking' table correctly
    """
    print('try to execute this')
    data = database.tracking.update_one({'_id' : ObjectId(trakingid)}, {'$set' : {'emailNotification' : trackingStatus, 'allEmailNotification' : allTrackingStatus}})
    if data.matched_count == 1 and data.modified_count == 1:
        return True
    elif data.matched_count == 0:
        return False
    
def setNotificationOneUser(id, notificationStatus):
    """
    perpose :
    response :
    """
    data = database.users.update_one({'_id' : ObjectId(id)}, {'$set' : {'allEmailNotification' : notificationStatus}})
    if data.acknowledged == True:
        return True
    elif data.acknowledged == False:
        return False