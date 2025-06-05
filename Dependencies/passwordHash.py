from passlib.hash import pbkdf2_sha256

def hashedPassword(password):
    return pbkdf2_sha256.hash(password)

# verified hashed password
def verifyPassword(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)