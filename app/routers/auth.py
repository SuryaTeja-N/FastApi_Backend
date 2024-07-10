from fastapi import FastAPI,Depends,Response,status,HTTPException,APIRouter
from sqlalchemy.orm import Session
from .. import database, schemas , models, utils
from .. import oauth2

router = APIRouter(tags=["Authentication"]) #tag are for documentation purposes

@router.post("/login", response_model = schemas.token)
def user_login(req : schemas.userlogin, db : Session = Depends(database.get_db)):
    user = db.query(models.users).filter(models.users.email == req.email).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "user not found")
    if not utils.verify_password(req.password, user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "incorrect password")
    
    access_token = oauth2.create_access_token(data = {"user_id" : user.id})

    return {"access_token" : access_token, "token_type" : "bearer"}
