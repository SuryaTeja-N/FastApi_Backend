import jwt,os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 

#lets create a method to verify the token
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : str = payload.get("user_id") #remember, we have generated this using user_id, check in auth.py
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id = id)

    except InvalidTokenError:
        raise credentials_exception

    return token_data
    


#now we will write a method which will check if the token is valid or not for every request
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login") #to match with auth.py 's login route

def get_current_user(token: str = Depends(oauth_scheme), db : Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)

    user = db.query(models.users).filter(models.users.id == token.id).first()

    return user

