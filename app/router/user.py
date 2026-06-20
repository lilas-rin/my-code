from fastapi import FastAPI, HTTPException, Response, status, Depends,APIRouter
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db
from app import utils

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 创建用户
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # 将 Pydantic 对象转成字典
    user_data = user.model_dump()

    # 对密码进行哈希加密
    user_data["password"] = utils.hash(user.password)

    # 创建数据库对象
    new_user = models.User(**user_data)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# 查询全部用户
@router.get(
    "/",
    response_model=list[schemas.UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()
    return users


# 根据 id 查询单个用户
@router.get(
    "/{id}",
    response_model=schemas.UserResponse
)
def get_user(
    id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} was not found"
        )

    return user


# 根据 id 删除用户
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
    id: int,
    db: Session = Depends(get_db)
):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} was not found"
        )

    user_query.delete(synchronize_session=False)
    db.commit()

    return

# 修改用户密码
@router.put(
    "/{id}/password",
    status_code=status.HTTP_200_OK
)
def update_password(
    id: int,
    password_data: schemas.UserUpdatePassword,
    db: Session = Depends(get_db)
):
    # 查询用户是否存在
    user = db.query(models.User).filter(
        models.User.id == id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} was not found"
        )

    # 校验旧密码
    if not utils.verify(
        password_data.old_password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    # 校验两次新密码是否一致
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The two new passwords do not match"
        )

    # 更新密码（重新加密）
    user.password = utils.hash(password_data.new_password)

    db.commit()
    db.refresh(user)

    return {
        "message": "Password updated successfully"
    }