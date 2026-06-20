from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, conint


class PostModel(BaseModel):
    title: str
    content: str
    published: bool = True


class CreatedPosts(PostModel):
    pass


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class Post(PostModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse


class PostWithVotes(Post):
    votes: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
