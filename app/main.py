from typing import List, Optional
from fastapi import Depends, FastAPI, Response, Body, HTTPException,status
from pydantic import BaseModel
from random import randint
import psycopg2
import psycopg2.extras
import time
from . import models,schemas,utils
from .database import engine,get_db
from sqlalchemy.orm import Session
from .routers import posts,users,auth,vote


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# myposts = [ {"title": "my first post", "content": "my first content", "id": 1} ,
#             {"title": "my second post", "content": "my second content", "id": 2}
#          ]


app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)






