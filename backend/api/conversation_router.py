from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

# 数据库会话依赖
from database.connect import get_db
# 用户鉴权依赖
from api.common import get_current_user
# CRUD操作
from database.crud_conversation import (
    create_conversation,
    get_session_conversations,
    get_user_all_session_ids,
    get_user_session_list,
    delete_session_conversation,
    delete_user_all_conversation
)
# 数据模型
from schemas.conversation_schema import ConversationCreate, ConversationItem, SessionListResp

router = APIRouter(prefix="/conversation", tags=["对话会话模块"])

# 新增 SessionList 响应模型
class SessionInfo(BaseModel):
    session_id: str
    last_time: str
    msg_count: int
    preview: str

class SessionListResult(BaseModel):
    sessions: List[SessionInfo]

# 1. 新增一条对话消息
@router.post("/add", response_model=ConversationItem)
def add_conversation(
    conv_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_uid: int = Depends(get_current_user)
):
    return create_conversation(
        db=db,
        user_id=current_uid,
        session_id=conv_data.session_id,
        role=conv_data.role,
        content=conv_data.content,
        portrait_json=conv_data.portrait_json
    )

# 2. 查询单个会话全部对话记录
@router.get("/session/{session_id}", response_model=List[ConversationItem])
def get_one_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_uid: int = Depends(get_current_user)
):
    return get_session_conversations(db, current_uid, session_id)

# 3. 查询用户所有会话ID列表
@router.get("/session/list", response_model=SessionListResp)
def get_all_session(
    db: Session = Depends(get_db),
    current_uid: int = Depends(get_current_user)
):
    session_ids = get_user_all_session_ids(db, current_uid)
    return {"session_ids": session_ids}

# 3.5 获取用户会话列表（含预览）
@router.get("/sessions", response_model=SessionListResult)
def get_sessions_with_preview(
    db: Session = Depends(get_db),
    current_uid: int = Depends(get_current_user)
):
    sessions = get_user_session_list(db, current_uid)
    return {"sessions": sessions}

# 4. 删除指定会话全部消息
@router.delete("/session/{session_id}")
def del_one_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_uid: int = Depends(get_current_user)
):
    delete_session_conversation(db, current_uid, session_id)
    return {"msg": "当前会话对话已清空"}

# 5. 清空用户全部对话记录
@router.delete("/all")
def del_all_conversation(
    db: Session = Depends(get_db),
    current_uid: int = Depends(get_current_user)
):
    delete_user_all_conversation(db, current_uid)
    return {"msg": "您所有对话记录已清空"}