from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from Schemas import User, Credentials
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from jose import jwt, ExpiredSignatureError
from typing import Annotated
from passlib.hash import pbkdf2_sha256

bare = HTTPBearer()

load_dotenv()
auth = APIRouter()
security = HTTPBearer()

# mondoDB database config 
load_dotenv()
mongo = MongoClient(os.getenv('mongo'))
cluster = mongo['price_platform']
users = cluster['user']


# ------------------------------------------------------
# side support functions

# get hashed password
def hashedPassword(password):
    return pbkdf2_sha256.hash(password)

# verified hashed password
def verifyPassword(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

def encriptJWT(data):
    return jwt.encode(data, os.getenv('jwt'), algorithm='HS256')

def decriptJWT(Token):
    try:
        return jwt.decode(Token, os.getenv('jwt'), algorithms='HS256')
    except ExpiredSignatureError as e:
        return e


def authVerification(details : Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    return decriptJWT(details.credentials)


# ------------------------------------------------------
# create new user
@auth.post('/create-user',tags=['user-auth'])
async def createUser(user : User):
    # find duplicate username or email
    userInfo = users.find_one({'email' : user.email})
    # if email not duplicate
    if userInfo == None:
        # get hashed password
        hashedPass = hashedPassword(user.password)
        # insert data into database
        users.insert_one({'email' : user.email, 'first_name' : user.first_name, 'password' : hashedPass, 'created' : user.created, 'product' : []})
        data = {'email' : user.email, 'password' : user.password}
        token = encriptJWT(data)
        return JSONResponse(status_code=200, content={'message' : 'account created', 'token' : token})
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
        # unhashed password
        unhashedPass = verifyPassword(credentials.password, userDetails['password'])
        # get verified password 
        if unhashedPass == True:
            data = {'email' : userDetails['email'], 'password' : userDetails['password']}
            token = encriptJWT(data)
            return JSONResponse(status_code=200, content={'name' : userDetails['first_name'], 'token' : token})
        else:
            return JSONResponse(status_code=404, content={'error' : "password not mached"})
    else:
        return JSONResponse(status_code=404, content={'message' : 'something go wrong'})


@auth.post('/remove-account', summary='this is for remove email and all tracked emails')
async def removeAccount(token = Depends(authVerification)):
    deletedDetails = users.delete_one({'email' : token['email']})
    if deletedDetails.deleted_count > 0:
        return JSONResponse(status_code=200, content={'message' : 'deleted successfully'})
    else:
        return JSONResponse(status_code=401, content={'error' : 'not found'})

@auth.post('/account-data', summary='this is for get details about user profile')
async def userAccount(token = Depends(authVerification)):
    userDetials = users.find_one({'email' : token['email']})
    userDetials['_id'] = str(userDetials['_id'])
    return JSONResponse(status_code=200, content={
        '_id' : userDetials['_id'],
        'email' : userDetials['email'],
        'first_name' : userDetials['first_name']
    })