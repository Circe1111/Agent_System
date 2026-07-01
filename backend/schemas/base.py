from pydantic import BaseModel
from datetime import datetime

# 用户基础校验模型
class UserBase(BaseModel):
    username: str
    nickname: str | None = None
    major: str | None = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    create_time: datetime
    class Config:
        orm_mode = True