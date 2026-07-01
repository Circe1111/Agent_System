from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models import EduUser, EduChat, Students, EduResource, LearningRecords

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 根据用户名查询用户
def get_user_by_username(db: Session, username: str):
    return db.query(EduUser).filter(EduUser.username == username).first()

# 根据ID查询用户
def get_user_by_id(db: Session, user_id: int):
    return db.query(EduUser).filter(EduUser.id == user_id).first()

# 新增用户
def create_user(db: Session, user_data: dict):
    if "password" in user_data and user_data["password"]:
        user_data = {**user_data, "password": hash_password(user_data["password"])}
    db_user = EduUser(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user