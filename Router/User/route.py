from fastapi import APIRouter, Depends
from Dependencies import JWTtoken
from . import db   
from fastapi.responses import JSONResponse
from datetime import datetime

user = APIRouter(prefix='/user')

@user.get('/details', tags=['user'])
async def getUserDeails(credencial = Depends(JWTtoken.authVerification)):
    # check credentials
    if credencial == False:
        return JSONResponse(status_code=404, content={'message' : "unauthorised"})
    elif credencial != False:
        # find the user account base on token's detials
        user = db.userDetails(credencial['email'])
        if user == False:
            # responsess
            return JSONResponse(status_code=400, content={'message' : 'account not found'})
        elif user != False:
            # searialize data
            user['_id'] = str(user['_id'])
            user['createdAt'] = str(user['createdAt'].date())
            return JSONResponse(status_code=200, content={"message" : 'successfull', 'data' : user})
        
@user.patch('/setnotificationall', tags=['user'])
async def setNotificationAll(notificationStatus:bool, credencials = Depends(JWTtoken.authVerification)):
    # validate credentials
    if credencials != False:
        # get the userId using credencials' email
        userId = db.userDetails(credencials['email'])
        if userId == False:
            # update the tracking tables' 'emailNotification' to false
            return JSONResponse(status_code=400, content={'message' : 'email not found'})
        elif userId != False:
            # swap the value of the "notificationStatus"
            notificationStatus = not notificationStatus 
            # if all are correct, then set 'True' on 'emailNotification' in User table
            notification = db.setNotificationOnTracks(userId['_id'], notificationStatus)
            print(f'all tracks updated {notification}')
            if notification == True:            
                userUpdate = db.setNotificationOneUser(userId['_id'], notificationStatus)
                print(f'user details updated {userUpdate}')
                if userUpdate == True:
                    # send responds
                    return JSONResponse(status_code=200, content={'message' : 'succesful'})
                else:
                    return JSONResponse(status_code=500, content={'message' : 'something go wrong', 'code' : 1000})
            else:
                return JSONResponse(status_code=500, content={'message' : 'something go wrong', 'code' : 1001})
    elif credencials == False:
        return JSONResponse(status_code=404, content={'messgae' : 'unauthonticated'})
    
@user.patch('/setnotification', tags=['user'])
async def setNotification(trakingId : str, trackingStatus:bool, allTrackingStatus : bool, credencials = Depends(JWTtoken.authVerification)):
    # check credencials
    if credencials != False:

        # defined the final output ( allEmailNotification + emailNotification )
        if allTrackingStatus == False:
            trackingStatus = True
            allTrackingStatus = True
            update = db.setNotificationOnTrack(trakingId, trackingStatus, allTrackingStatus)
        
        elif allTrackingStatus == True:
            trackingStatus = not trackingStatus
            update = db.setNotificationOnTrack(trakingId, trackingStatus, allTrackingStatus)

        # udpate 'tracking' table
        if update == True:
            # response
            return JSONResponse(status_code=200, content={'message' : 'successful'})
        elif update == False:
            return JSONResponse(status_code=400, content={'message' : 'cannot locate tracking product'})
    elif credencials == False:
        return JSONResponse(status_code=404, content={'message' : 'unauthorized'})