from fastapi import APIRouter
from Schemas import User, Credentials
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()
auth = APIRouter()

# mondoDB database config 
load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
cluster = mongo['price_platform']
users = cluster['user']

# ------------------------------------------------------
# create new admin user
@auth.post('/create-user',tags=['user-auth'])
async def createUser(user : User):
    # find duplicate username or email
    userInfo = users.find_one({'email' : user.email})
    # if email not duplicate
    if userInfo == None:
        users.insert_one({'email' : user.email, 'first_name' : user.first_name, 'password' : user.password, 'created' : user.created})
        return JSONResponse(status_code=200, content={'message' : 'account create succesfully'})
    # if username or mail duplicate
    else:
        return JSONResponse(status_code=400, content={'error' : 'duplicated'})
        

# user login
@auth.post('/login', tags=['user-auth'])
async def login(credentials: Credentials):
    # find user by usernam in database
    userDetails = users.find_one({'email': credentials.email})
    # if user found
    if userDetails != None:
        # get verified password 
        if credentials.password == userDetails['password']:
            return JSONResponse(status_code=200, content={'message' : 'successful'})
        else:
            return JSONResponse(status_code=404, content={'error' : "password not mached"})

