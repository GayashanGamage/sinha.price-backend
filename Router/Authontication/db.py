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
    
def storeScreateCode(email, code):
    """
    set the secrete code in cache memory
    return - True : store successfull | False : not successfull
    """
    setData = cache.cache.hset(f'{cache.verification}:{email}', mapping={'code' : f'{code}', 'verified' : f'{False}'})
    print(setData)
    if setData == 2:
        print(f"cache secreate code related to {email} email address")
        return True
    else:
        print(f"caching attempt of the secrete code of the {email} unsucessfull")
        return False
    
def storeMailDate(data):
    """
    store verification email send details
    return - true : successfull | false : unsuccessfull
    """
    print(data)
    mailData = database.passwordreset.insert_one(data.dict())
    if mailData.acknowledged == True:
        print("send email for password-reset transaction recode in successfull")
        return True
    else:
        print("send email for password-reset transaction recode in NOT-successfull")
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