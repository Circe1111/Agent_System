from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
from database.connect import get_db
from database import crud
from schemas.base import UserCreate, UserOut
from api.common import create_token, get_current_user
from utils.response import success
from utils.exception import ApiException

router = APIRouter(prefix="/user", tags=["用户模块"])

@router.options("/register")
def register_options(request: Request):
    return {"status": "ok"}

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise ApiException(code=400, msg="用户名已存在")
    new_user = crud.create_user(db, user.model_dump())
    return success(data=UserOut.model_validate(new_user).model_dump())

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if not user or not crud.verify_password(password, user.password):
        raise ApiException(400, "账号密码错误")
    token = create_token(user.id)
    return success(data={"token": token})

@router.get("/info")
def user_info(uid: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, uid)
    if not user:
        raise ApiException(404, "用户不存在")
    return success(data=UserOut.model_validate(user).model_dump())