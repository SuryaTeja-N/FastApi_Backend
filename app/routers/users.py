from .. import models,schemas,utils
from ..database import engine,get_db
from fastapi import FastAPI,Depends,Response,status,HTTPException,APIRouter
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(tags=["Users"]) #tag are for documentation purposes


# now, lets deal with user account creation & login with new users table

@router.post("/users/create", status_code = status.HTTP_201_CREATED, response_model = schemas.usercreate_response)
def create_user(req : schemas.usercreate, db: Session = Depends(get_db)):
   #lets hash the user given password
   hashed_password = utils.get_password_hash(req.password)
   req.password = hashed_password

   new_user = models.users(**req.dict())
   db.add(new_user)
   db.commit()
   db.refresh(new_user)

   return new_user

@router.get("/users/get/{id}",response_model=schemas.userget_response)
def get_user(id : int, db: Session = Depends(get_db)):
    user = db.query(models.users).filter(models.users.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="the user you requested is not found")
    return user