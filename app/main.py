from fastapi import FastAPI, HTTPException, Response, status, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from app.router import user
from app.router import posts
from app.router import auth
from app.router import vote


app = FastAPI()
# 限制可以访问api的范围
#如果后续前端有域名请添加上去
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",

]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载user接口
app.include_router(user.router)
# 挂载posts接口
app.include_router(posts.router)
# 挂载auth接口
app.include_router(auth.router)
# 挂载vote接口
app.include_router(vote.router)


@app.get("/")
def welcome():
    return {"mes": "我在你们这里买东西已经发现了三个问题,是的是的"}
