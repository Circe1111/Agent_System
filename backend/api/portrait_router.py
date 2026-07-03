from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from database.connect import get_db
from api.common import get_current_user
from database.crud_profile import get_user_profile, update_user_profile, get_full_profile
from database.crud_conversation import get_user_all_conversations
from services.llm_utils import analyze_learning_style_from_history, get_default_style_analysis
from utils.response import success

router = APIRouter(prefix="/portrait", tags=["用户画像模块"])


@router.get("/me")
def get_my_user_portrait(
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    full = get_full_profile(db=db, user_id=current_login_uid)
    return success(data={"portrait": full})


@router.post("/update")
def update_my_user_portrait(
    req_body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    portrait_data = req_body.get("portrait_json") or req_body
    updated = update_user_profile(
        db=db,
        user_id=current_login_uid,
        portrait_data=portrait_data
    )
    full = get_full_profile(db=db, user_id=current_login_uid)
    return success(data={"portrait": full})


@router.post("/analyze-style")
def analyze_learning_style(
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    conversations = get_user_all_conversations(db=db, user_id=current_login_uid)

    if not conversations or len(conversations) < 2:
        result = get_default_style_analysis()
        result["analysis_summary"] = "对话数据不足，请先与AI助手进行一些学习相关的对话。"
        return success(data={"style_analysis": result})

    dialogue_lines = []
    for c in conversations[-50:]:
        role_label = "学生" if c["role"] == "user" else "AI助手"
        dialogue_lines.append(f"{role_label}：{c['content']}")
    dialogue_text = "\n".join(dialogue_lines)

    result = analyze_learning_style_from_history(dialogue_text)
    if result is None:
        result = get_default_style_analysis()

    return success(data={"style_analysis": result})