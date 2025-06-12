from jose import jwt, ExpiredSignatureError
import os
from fastapi import Depends
from typing import Annotated
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def encriptJWT(email):
    data = {'email' : email}
    return jwt.encode(data, os.getenv('jwt'), algorithm='HS256')

def decriptJWT(Token):
    try:
        return jwt.decode(Token, os.getenv('jwt'), algorithms='HS256')
    except ExpiredSignatureError as e:
        return e

def authVerification(details : Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    try:
        return decriptJWT(details.credentials)
    except:
        return False