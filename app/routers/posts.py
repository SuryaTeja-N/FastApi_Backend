from typing import List, Optional
from fastapi import Depends, FastAPI, Response, Body, HTTPException,status, APIRouter
from .. import models,schemas,utils,oauth2
from ..database import engine,get_db
import psycopg2,psycopg2.extras
import time,os
from sqlalchemy import func
from sqlalchemy.orm import Session
from os import getenv

router = APIRouter(tags=["Posts"]) #tag are for documentation purposes

while True:
    try:
        connection = psycopg2.connect(host = os.getenv("host"), database = os.getenv("database"), user = os.getenv("user"),
                                    password = os.getenv("password"), cursor_factory= psycopg2.extras.RealDictCursor)
        cursor = connection.cursor()
        print("Database connected successfully")
        break
    except Exception as error:
        print("Error while connecting to database", error)
        time.sleep(2)

@router.get("/get_posts", response_model=List[schemas.post_resonse])
def get_posts():
    cursor.execute("""select * from posts""")
    all_posts = cursor.fetchall()
    return all_posts

@router.post("/create_post", status_code = status.HTTP_201_CREATED, response_model = schemas.post_resonse)
def create_post(body : schemas.createpost, curr_user : int = Depends(oauth2.get_current_user)):
    #cursor.execute("""insert into posts (title, content, published) values (body.title, body.content, body.published)""")
    #above will cause sql injection
    cursor.execute("""insert into posts (title, content, published, user_id) values (%s, %s, %s, %s) returning *""",
                   (body.title, body.content, body.published, str(curr_user.id)))
    created_post = cursor.fetchone()
    connection.commit() 
    return created_post

@router.get("/get_post/{id}",response_model=schemas.post_resonse)
def get_post(id : int): # we need to have in int only, beacuse user potentially can give some string
    cursor.execute("""select * from posts where id = %s""", (str(id)))
    gotten_post = cursor.fetchone()
    if not gotten_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "the post you requested is not found")
    return gotten_post

@router.delete("/delete_post/{id}")
def delete_post(id : int, curr_user : int = Depends(oauth2.get_current_user)):
    # lets get the user id for the given post id
    cursor.execute("""select * from posts where id = %s""", (str(id)))
    gotten_post = cursor.fetchone()
    if curr_user.id != gotten_post["user_id"]:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                            detail = "Not authorized to perform requested action")
    cursor.execute("""delete from posts where id = %s returning *""", (str(id)))
    deleted_post = cursor.fetchone()
    connection.commit()
    if not deleted_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "the post you requested is not there to delete it")
    return {"message" : f"post with id : {id} deleted successfully"}
    

@router.put("/update_post/{id}")
def update_post(id : int, body : schemas.createpost, curr_user : int = Depends(oauth2.get_current_user)):
    # lets get the user id for the given post id
    cursor.execute("""select * from posts where id = %s""", (str(id)))
    gotten_post = cursor.fetchone()
    if gotten_post["user_id"] != curr_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                            detail = "Not authorized to perform requested action")
    cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""",
                    (body.title, body.content, body.published, str(id)))
    updated_post = cursor.fetchone()
    connection.commit()
    if not updated_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "the post you requested is not there to update it")
    return {"message" : f"post with id : {id} updated successfully"}    
  

# ORM stuff ( using sqlalchemy ) same as above with different api endpoints

# @router.get("/sqlalchemy/getposts", response_model=List[schemas.post_with_ownerdetail])
@router.get("/sqlalchemy/getposts", response_model=List[schemas.post_withvotes])
def orm_getposts(db: Session = Depends(get_db), limit : int = 5,
                  skip : int = 0, search : Optional[str] = ""):
    #all_posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts_withvotes = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts_withvotes

@router.post("/sqlalchemy/createpost", status_code = status.HTTP_201_CREATED, response_model = schemas.post_with_ownerdetail)
def orm_createpost(post : schemas.createpost, db: Session = Depends(get_db), curr_user : int = Depends(oauth2.get_current_user)):
    dic = post.dict()
    new_post = models.Post(user_id = curr_user.id, **dic) #unpacking the dictionary to push it in db
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/sqlalchemy/getpost/{id}",response_model=schemas.post_withvotes)
def orm_getpost(id : int, db: Session = Depends(get_db)):
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "the post you requested is not found")
    return post

@router.delete("/sqlalchemy/deletepost/{id}")
def orm_deletepost(id : int, db: Session = Depends(get_db), curr_user : int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "the post you requested is not there to delete it")
    if post.user_id != curr_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                            detail = "you are not allowed to delete this post")
    db.delete(post)
    db.commit()
    return {"message" : f"post with id : {id} deleted successfully"}

@router.put("/sqlalchemy/updatepost/{id}")
def orm_updatepost(id : int, post : schemas.createpost, db: Session = Depends(get_db), curr_user : int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    old_post = post_query.first()
    if not old_post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = "the post you requested is not there to update it")
    if old_post.user_id != curr_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,
                            detail = "you are not allowed to delete this post")
    post_query.update(post.dict() , synchronize_session = False)
    db.commit()
    return {"message" : f"post with id : {id} updated successfully"}