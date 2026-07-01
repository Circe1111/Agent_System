from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import EventSourceResponse

from api.common import get_current_user
from database.connect import get_db
from schemas.chat_schema import StreamChatRequest
from database.crud_conversation import create_conversation
from services.stream_service import stream_chat_response

router = APIRouter(prefix="/api/v1/chat", tags=["SSE流式AI对话"])

@router.post("/stream", response_class=EventSourceResponse, summary="流式打字机对话接口")
async def chat_stream(
    req: StreamChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    业务逻辑：
    1.JWT鉴权，获取当前登录用户ID
    2.存储用户提问至conversation对话表
    3.SSE流式分段返回AI回答（打字机效果）
    4.对话全部结束后自动抽取学生画像，更新students表
    """
    user_id = current_user
    sess_id = req.session_id
    user_text = req.user_content

    # 持久化用户提问
    create_conversation(
        db=db,
        user_id=user_id,
        session_id=sess_id,
        role="user",
        content=user_text
    )

    # 返回SSE流式数据流
    generator = stream_chat_response(
        session_id=sess_id,
        user_msg=user_text,
        user_id=user_id,
        db=db
    )
    return EventSourceResponse(generator)