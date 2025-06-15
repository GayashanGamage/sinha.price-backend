from Dependencies.database import DB

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
    