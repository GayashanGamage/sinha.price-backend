from Dependencies.database import DB, Redis
from pymongo import ReturnDocument

database = DB()
cache = Redis()


def checkDuplicateUser(email):
    """
    check dubplicate users in the database
    """
    existingUser = database.users.find_one({'email' : email})
    if existingUser == None:
        print(f"there is a user under { email } email address")
        return False
    else:
        print(f"there is no any user under { email } email address")
        return True
    
def addNewUser(userData):
    """
    insert new user 
    """
    newUser = database.users.insert_one(userData.model_dump())
    if newUser.acknowledged == True:
        print(f"{userData.email} insert as new user")
        return newUser.inserted_id
    else:
        print(f"{userData.email} cannot inset as new user - Error")
        return False
    
def checkEmail(email):
    """
    check email is available or not
    return - false : account is not avialable | userDetails : email is match 
    """
    userDetails = database.users.find_one({'email' : email})
    if userDetails == None:
        print(f'{email} doesnt exisit as a user')
        return False
    else:
        print(f'{email} is exisit as a user.')
        return userDetails
    
def clearCacheVerificationData(email):
    """
    perpose : remove unused password change verification codes
    response : True : old data record available | False : old data records not available
    """
    data = cache.cache.delete(f'{cache.verification}:{email}')
    if data == 0:
        return False
    elif data == 1:
        return True

def addPasswordResetRecodeDB(email):
    """
    perpose : add password reset recode in to database ( mongodb )
    response : True : add recode successful | False : cannot add recode in to database
    """
    data = database.passwordreset.insert_one(email.dict())
    if data.acknowledged == True:
        return True
    else:
        return False
    
def addPasswordResetRecodeCache(email, secreateKey):
    """
    perpose : add password reset recode in to cache
    response : True : add recode successful | False : cannot add recode in to database
    """
    data = cache.cache.hset(f'{cache.verification}:{email}', mapping={'code' : f'{secreateKey}', 'verifiede' : f'{False}'})
    if data == 2:
        return True
    elif data == 0:
        return False
    
def emailValidation(credencials):
    """
    check the email on redis verification list. if so then set 'verified' field 'True'
    return - True : all successful | False : invalied key | 1001 : cannot update verified to "True" | 1002 : email not available in 'verification' on redis
    """
    cacheData = cache.cache.hget(f'{cache.verification}:{credencials.email}', 'code')
    print(cacheData, credencials.code)
    if cacheData == None:
        return 1002
    elif int(cacheData) == credencials.code:
        changeCacheData = cache.cache.hset(f'{cache.verification}:{credencials.email}', 'verified', f'{True}')
        print(changeCacheData)
        if changeCacheData == 0:
            return True 
        else:
            return 1001
    elif int(cacheData) != credencials.code:
        return False
    
def checkEmailVerification(email):
    """
    check the email is available in 'verification' on redis and verified or not ?
    output : True : verified | False : not verified | 1000 : email not available on 'verification' - redis
    """
    status = cache.cache.hget(f'{cache.verification}:{email}', 'verified')
    if status == None:
        print(f'{email} is not available on redis "verification" section')
        return 1000
    elif bool(status) == True:
        print(f'{email} is verified')
        return True
    elif bool(status) == False:
        print(f'{email} is not verified')
        return False
    
def updatePassword(credencials):
    """
    perpose : check the email is available on database and then update the password
    output : True : password update successufully | False : email not found | 1000 : document found, but update not happend
    """
    changePassword = database.users.find_one_and_update({'email' : credencials.email}, {'$set' : {'password' : credencials.password}}, return_document=ReturnDocument.AFTER)
    if changePassword == None:
        print(f'{credencials.email} not found on "User" collection')
        return False
    elif changePassword['password'] == credencials.password:
        print(f'password updated successfully on {credencials.email}')
        return True
    elif changePassword['password'] != credencials.password:
        print(f'{credencials.email} found on "User" collection, but not updated properly')
        return 1000
    
def removeVerificationOnRedis(email):
    """
    perpose : remove password reset related data on redis 'verification' section
    return - True : successfull | false : not succesfull
    """
    removeData = cache.cache.hdel(f'{cache.verification}:{email}', 'code', 'verified')
    if removeData == 2:
        return True
    else:
        return False