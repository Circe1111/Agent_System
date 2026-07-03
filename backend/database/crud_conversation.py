from sqlalchemy.orm import Session
from database.models import Conversation
from sqlalchemy import desc, func
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))

def _fmt_time(dt):
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt.isoformat()

def _conv_to_dict(conv):
    return {
        "id": conv.id,
        "user_id": conv.user_id,
        "session_id": conv.session_id,
        "role": conv.role,
        "content": conv.content,
        "portrait_json": conv.portrait_json,
        "create_time": _fmt_time(conv.create_time),
    }

# 1. 新增一条对话消息
def create_conversation(
    db: Session,
    user_id: int,
    session_id: str,
    role: str,
    content: str,
    portrait_json: dict = None
):
    db_conv = Conversation(
        user_id=user_id,
        session_id=session_id,
        role=role,
        content=content,
        portrait_json=portrait_json,
        create_time=datetime.now(TZ)
    )
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    return db_conv

# 2. 根据会话ID，查询该会话下所有对话（按时间正序，最早在前）
def get_session_conversations(db: Session, user_id: int, session_id: str):
    convs = db.query(Conversation)\
        .filter(Conversation.user_id == user_id, Conversation.session_id == session_id)\
        .order_by(Conversation.create_time)\
        .all()
    return [_conv_to_dict(c) for c in convs]

# 3. 查询用户全部会话（去重session_id）
def get_user_all_session_ids(db: Session, user_id: int):
    res = db.query(Conversation.session_id)\
        .filter(Conversation.user_id == user_id)\
        .distinct()\
        .all()
    return [row[0] for row in res]

# 4. 获取用户会话列表（含预览信息）
def get_user_session_list(db: Session, user_id: int):
    subs = db.query(
        Conversation.session_id,
        func.max(Conversation.create_time).label("last_time"),
        func.count(Conversation.id).label("msg_count")
    ).filter(
        Conversation.user_id == user_id
    ).group_by(
        Conversation.session_id
    ).order_by(
        desc("last_time")
    ).all()

    result = []
    for sub in subs:
        first_msg = db.query(Conversation)\
            .filter(Conversation.user_id == user_id, Conversation.session_id == sub.session_id)\
            .order_by(Conversation.create_time)\
            .first()
        preview = (first_msg.content[:30] + "...") if first_msg and len(first_msg.content) > 30 else (first_msg.content if first_msg else "")
        result.append({
            "session_id": sub.session_id,
            "last_time": _fmt_time(sub.last_time),
            "msg_count": sub.msg_count,
            "preview": preview,
        })
    return result

# 5. 删除单个会话所有对话
def delete_session_conversation(db: Session, user_id: int, session_id: str):
    db.query(Conversation)\
        .filter(Conversation.user_id == user_id, Conversation.session_id == session_id)\
        .delete()
    db.commit()
    return True

# 6. 删除用户全部对话记录
def delete_user_all_conversation(db: Session, user_id: int):
    db.query(Conversation).filter(Conversation.user_id == user_id).delete()
    db.commit()
    return True


# 7. 获取用户全部对话记录（按时间正序）
def get_user_all_conversations(db: Session, user_id: int):
    convs = db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.create_time)\
        .all()
    return [_conv_to_dict(c) for c in convs]