from Dependencies.database import DB, Redis

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
    setData = cache.cache.set(f"{cache.verification}:{email}", code)
    if setData == True:
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