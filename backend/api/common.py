import os
import sys
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from database.crud import get_user_by_id

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY or JWT_SECRET_KEY.startswith("change-"):
    print(
        "ERROR: JWT_SECRET_KEY is not set or still uses default value. Please set it in .env",
        file=sys.stderr,
    )
    sys.exit(1)

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def create_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = int(payload.get("sub"))
        if uid is None:
            raise HTTPException(status_code=401, detail="token无效")
    except Exception:
        raise HTTPException(status_code=401, detail="token过期或错误")
    return uid