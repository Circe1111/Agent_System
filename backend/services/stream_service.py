import json
import asyncio
import logging
from typing import AsyncGenerator
from fastapi.responses import EventSourceResponse
from sqlalchemy.orm import Session

# 项目内部依赖
from database.crud_conversation import create_conversation
from database.crud_profile import get_user_profile, update_user_profile
from services.llm_utils import extract_profile, get_default_profile
from services.llm_agent import chat_stream as _llm_chat_stream

logger = logging.getLogger(__name__)

def format_sse(data: dict) -> str:
    """标准SSE返回格式"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

# 异步流式大模型调用 — 走统一的 OpenAI 兼容接口
async def _chat_stream_local(messages, temperature=0.7, max_tokens=4096, **_ignored):
    async for token in _llm_chat_stream(
        messages, temperature=temperature, max_tokens=max_tokens
    ):
        yield token

# 包装D的同步画像抽取函数，转为异步（不改动源文件）
async def extract_portrait_prompt(dialogue_text: str):
    profile_dict = await asyncio.to_thread(extract_profile, dialogue_text)
    if not profile_dict:
        return get_default_profile()
    return profile_dict

# 流式对话主生成器，接口调用入口
async def stream_chat_response(
    session_id: str,
    user_msg: str,
    user_id: str,
    db: Session
) -> AsyncGenerator[str, None]:
    full_ai_reply = ""
    try:
        # 获取当前用户已有画像
        student_info = get_user_profile(db=db, user_id=user_id)
        if student_info:
            info_dict = {k: v for k, v in student_info.__dict__.items() if not k.startswith("_")}
            portrait_context = json.dumps(info_dict, ensure_ascii=False, default=str)
        else:
            portrait_context = "暂无学生学习画像"
        # 组装大模型上下文
        messages = [
            {"role": "system", "content": f"根据以下学生画像进行个性化答疑：{portrait_context}"},
            {"role": "user", "content": user_msg}
        ]
        # 逐token流式推送
        async for token in _chat_stream_local(messages):
            full_ai_reply += token
            yield format_sse({"type": "delta", "content": token})
            await asyncio.sleep(0.005)
        # 保存AI回复到对话表
        create_conversation(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=full_ai_reply
        )
        # 整合对话抽取画像
        all_dialog = f"用户提问：{user_msg}\nAI回答：{full_ai_reply}"
        portrait_result = await extract_portrait_prompt(all_dialog)
        # 更新学生画像表
        update_user_profile(db=db, user_id=user_id, portrait_data=portrait_result)
        # 推送结束标识
        yield format_sse({"type": "done"})
    except Exception as e:
        logger.error(f"流式对话全局异常：{str(e)}")
        yield format_sse({"type": "error", "msg": f"对话服务异常：{str(e)}"})