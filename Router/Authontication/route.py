from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from . import db
from . import schema
from Dependencies import passwordHash, email as emailService, JWTtoken
from random import randint

route = APIRouter(prefix='/auth')

@route.post('/create-user', tags=['auth'])
async def cerateUser(user : schema.User):
    # check duplicate user
    dubplicateUser = db.checkDuplicateUser(user.email)
    if dubplicateUser == False:
        # convert plain password into hashed password
        user.password = passwordHash.hashedPassword(user.password)
        # insert new user in to database
        insertNewUser = db.addNewUser(user)
        if insertNewUser == False:
            return JSONResponse(status_code=500, content={'message' : 'something go wrong - try again latter'})
        else:
            token = JWTtoken.encriptJWT(user.email)
            return JSONResponse(status_code=200, content={'message' : 'account created', 'token' : token})  
    else:
        return JSONResponse(status_code=400, content={'error' : 'duplicated'})
        

@route.post('/login', tags=['auth'])
async def userLogin(user : schema.UserOnlyCredintials):
    # check email is available or not
    userData = db.checkEmail(user.email)
    if userData == False:
        return JSONResponse(status_code=404, content={'message' : 'invalied credentials'})
    elif userData != False:
        passwordVerification = passwordHash.verifyPassword(user.password, userData['password'])
        if passwordVerification == True:
            return JSONResponse(status_code=200, content={'token' : JWTtoken.encriptJWT(user.email)})
        else:
            return JSONResponse(status_code=404, content={'message' : 'invalied credentials'})
            

@route.get('/sendverification', tags=['auth'])
async def sendVerificationCode(email : schema.emailVerification = Query()):
    # check the email is avalilable
    emailAvailability = db.checkEmail(email.email)
    if emailAvailability != False:
        db.clearCacheVerificationData(email.email)
        secreateKey = randint(1000, 9999)
        # this is for mongodb
        passwordResetRecodeDB = db.addPasswordResetRecodeDB(email) 
        # this is for redis
        passwordResetRecodeRedis = db.addPasswordResetRecodeCache(email.email, secreateKey)
        if passwordResetRecodeDB == True and passwordResetRecodeRedis == True:
            sendEmail = emailService.passwordReset(emailAvailability['firstName'], emailAvailability['email'], secreateKey)
            if sendEmail.message_id != None:
                return JSONResponse(status_code=200, content={'message' : 'send secreatecode successfully'})
            elif sendEmail.message_id == None:
                return JSONResponse(status_code=500, content={'message' : 'server error. try again'})
        else:
            return JSONResponse(status_code=500, content={'message' : 'sever error. try again'})
    else:
        return JSONResponse(status_code=400, content={'message' : 'invalied email address'})
        

@route.post('/emailVerification', tags=['auth'])
async def emailVerification(credentials : schema.EmailVerification):
    Evaluation = db.emailValidation(credentials)
    if Evaluation == True:
        return JSONResponse(status_code=200, content={'message' : 'email verified'})
    elif Evaluation == False:
        return JSONResponse(status_code=404, content={'message' : 'invalied verification code'})
    elif Evaluation == 1001:
        return JSONResponse(status_code=500, content={'message' : 'internal error. try again later'})
    elif Evaluation == 1002:
        return JSONResponse(status_code=400, content={'message' : 'Invalied email'})


@route.patch('/passwordChange', tags=['auth'])
async def passwrodChannge(credencials : schema.UserOnlyCredintials):
    # check email verification status
    emailVerificationStatus = db.checkEmailVerification(credencials.email)
    # if verified
    if emailVerificationStatus==True:
        # password encript
        encriptPassword = passwordHash.hashedPassword(credencials.password)
        # update password on db
        channgePassword = db.updatePassword(credencials.email, encriptPassword)
        # if password update successfull
        if channgePassword == True:
            # remove data on 'verificaition' - redis
            removeData = db.removeVerificationOnRedis(credencials.email)
            if removeData == True:
                # send successfull message
                return JSONResponse(status_code=200, content={'message' : 'password change successfully'})
            else:
                return JSONResponse(status_code=500, content={'messege' : "something go wrong on cache"})
        # else
        elif channgePassword == False:
            return JSONResponse(status_code=400, content={'message' : 'invalied email'})
            # show error
        elif channgePassword == 1000:
            return JSONResponse(status_code=500, content={'message' : 'something go wrong. try latter'})
    # else
    elif emailVerificationStatus == False:
        return JSONResponse(status_code=400, content={'message' : 'email is not varified'})
        # show errro
    elif emailVerificationStatus == 1000:
        return JSONResponse(status_code=400, content={'message' : 'invalied email addresss'})