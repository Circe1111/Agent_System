from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from database.connect import get_db
from api.common import get_current_user
from database.crud_profile import get_user_profile, update_user_profile
from schemas.portrait_schema import PortraitUpdate

router = APIRouter(prefix="/portrait", tags=["用户画像模块"])


@router.get("/me")
def get_my_user_portrait(
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    profile = get_user_profile(db=db, user_id=current_login_uid)
    if profile:
        return {
            "user_id": profile.id,
            "portrait_json": profile.raw_json or {},
        }
    return {"user_id": current_login_uid, "portrait_json": {}}


@router.post("/update")
def update_my_user_portrait(
    req_body: PortraitUpdate,
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    updated = update_user_profile(
        db=db,
        user_id=current_login_uid,
        portrait_data=req_body.portrait_json
    )
    return {
        "user_id": updated.id,
        "portrait_json": updated.raw_json or {},
    }
