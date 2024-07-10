from passlib.context import CryptContext


#for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

#to verify the given user password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)