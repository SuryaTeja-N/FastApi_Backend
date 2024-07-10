from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional




#lets create a post model (pydantic/semantic model) to validate the request body
class Post(BaseModel):
    title : str ; content : str
    #optional fields
    published : bool = True
    #rating : Optional[int] = None


class createpost(Post):
    # user_id : int
    pass


class post_resonse(Post):
    id : int
    #created_at : str # see now, created_at will hide for user response
    created_at : datetime
    user_id : int

    class Config:  # to convert sqlalchemy model to pydantic model
       orm_mode = True

class post_withvotes(BaseModel):
    Post : post_resonse
    votes : int

# class update_post(Post):
#     user_id : int
#     pass


#lest make schema for user login request
class usercreate(BaseModel):
    email : EmailStr
    password : str

class usercreate_response(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime
    class Config:  # to convert sqlalchemy model to pydantic model
       orm_mode = True

class userget_response(usercreate_response):
    pass
    
class userlogin(BaseModel):
    email : EmailStr
    password : str 

# schema for token
class token(BaseModel):
    access_token : str
    token_type : str


# schema for token data (when user send token along with payload (data))
class TokenData(BaseModel):
    id : Optional[int] = None


# for each post call in  ORM stuff, we cann show the owner details for each post also.. for that
class post_with_ownerdetail(post_resonse):
    owner : usercreate_response
    pass

# schema for vote
class Vote(BaseModel):
    post_id : int
    dir : int # 1 for upvote, -1 for downvote