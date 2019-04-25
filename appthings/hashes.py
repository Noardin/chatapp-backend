from passlib.hash import pbkdf2_sha256

def set_hash(password):
   return pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

def verify_hash(input, password):
    return pbkdf2_sha256.verify(input, password )