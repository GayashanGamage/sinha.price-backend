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
        