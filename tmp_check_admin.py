import os
os.chdir('backend')
from database.connect import SessionLocal
from database import crud

with SessionLocal() as db:
    user = crud.get_user_by_username(db, 'admin')
    print('user_exists', bool(user))
    if user:
        print('verify', crud.verify_password('123456', user.password))
