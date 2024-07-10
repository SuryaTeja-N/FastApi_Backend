from fastapi import Depends, FastAPI, Response, Body, HTTPException,status, APIRouter
from .. import models,schemas,utils,oauth2
from ..database import engine,get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/like", #prefix for all routes in this file
    tags=["Vote"]) #tag are for documentation purposes

@router.post("/", status_code = status.HTTP_201_CREATED)
def upvote(vote : schemas.Vote, db: Session = Depends(get_db), curr_user : int = Depends(oauth2.get_current_user)):
        
        #first we need to check if user sending valid post id, which is there in our database
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
        if not post:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "This post is not available")
    
        query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id ,
                                      models.Vote.user_id == curr_user.id ) #means this user already liked this post
        found_vote = query.first()

        if vote.dir == 1:
            if found_vote:
                raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = "You already liked this post")
            new_vote = models.Vote(post_id = vote.post_id, user_id = curr_user.id)
            db.add(new_vote)
            db.commit()
            return {"message" : "successfully upvoted"}
        else:
           if not found_vote:
             raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "You have not liked this post")
           query.delete(synchronize_session = False)
           db.commit()
           return {"message" : "successfully downvoted"}
        