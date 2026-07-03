import json
import asyncio
import logging
from typing import AsyncGenerator
from sqlalchemy.orm import Session

# 项目内部依赖
from database.crud_conversation import create_conversation, get_session_conversations
from database.crud_profile import update_user_profile, get_full_profile
from services.llm_utils import extract_profile, extract_vark, get_default_profile, get_default_vark, analyze_learning_style_from_history, get_default_style_analysis
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
async def extract_portrait_prompt(dialogue_text: str, context: str = ""):
    profile_dict = await asyncio.to_thread(extract_profile, dialogue_text, context)
    if not profile_dict:
        return get_default_profile()
    return profile_dict


async def extract_vark_prompt(dialogue_text: str, context: str = ""):
    vark_dict = await asyncio.to_thread(extract_vark, dialogue_text, context)
    if not vark_dict:
        return get_default_vark()
    return vark_dict


async def extract_style_analysis(dialogue_text: str):
    result = await asyncio.to_thread(analyze_learning_style_from_history, dialogue_text)
    if not result:
        return get_default_style_analysis()
    return result

# 流式对话主生成器，接口调用入口
async def stream_chat_response(
    session_id: str,
    user_msg: str,
    user_id: str,
    db: Session
) -> AsyncGenerator[str, None]:
    full_ai_reply = ""
    try:
        user_id_int = int(user_id)
        full_profile = get_full_profile(db=db, user_id=user_id_int)

        # 获取历史对话（最近 20 条）
        history = get_session_conversations(db=db, user_id=user_id_int, session_id=session_id)
        history_messages = []
        for msg in history[-20:]:
            role = "assistant" if msg["role"] == "assistant" else "user"
            history_messages.append({"role": role, "content": msg["content"]})

        if full_profile.get("username"):
            raw_json = full_profile.get("raw_json") or {}
            vark_scores = raw_json.get("vark_scores") or {}
            vark_info = ""
            if vark_scores:
                vark_map = {"V": "视觉型", "A": "听觉型", "R": "读写型", "K": "动觉型"}
                dominant = max(vark_scores, key=lambda k: vark_scores[k] if k in vark_map else 0, default="")
                dominant_label = vark_map.get(dominant, "")
                vark_parts = []
                for k, label in vark_map.items():
                    pct = int((vark_scores.get(k, 0) or 0) * 100)
                    if pct > 20:
                        vark_parts.append(f"{label}{pct}%")
                if vark_parts:
                    vark_info = f"VARK学习风格：{' + '.join(vark_parts)}，主导类型：{dominant_label}。请根据学生的VARK类型调整教学方式：视觉型多用图表/示意图，听觉型多用口语化解释/类比，读写型多给文字总结/笔记，动觉型多给练习/动手示例。"
            portrait_context = (
                f"学生姓名：{full_profile.get('username', '')}\n"
                f"专业：{full_profile.get('major', '未填写')}\n"
                f"知识基础：{full_profile.get('knowledge_level', '中等')}\n"
                f"学习偏好：{full_profile.get('learning_preference', '视觉型')}\n"
                f"薄弱知识：{full_profile.get('weak_knowledge', '未填写')}\n"
                f"学习目标：{full_profile.get('study_goal', '未填写')}\n"
                f"学习时间：{full_profile.get('study_time', '未填写')}\n"
                f"课程：{full_profile.get('course', '未填写')}\n"
                f"{vark_info}"
            )
        else:
            portrait_context = "暂无学生学习画像"

        # 组装大模型上下文（含历史对话）
        messages = [
            {"role": "system", "content": f"你是一个智能教育助手。请根据以下学生画像进行个性化答疑，称呼学生的名字，使用亲切友好的语气。\n\n{portrait_context}"},
        ]
        messages.extend(history_messages)
        messages.append({"role": "user", "content": user_msg})
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
        # 从用户消息中抽取画像（只分析用户提问，不管AI回复）
        user_msgs = [msg["content"] for msg in history_messages if msg["role"] == "user"]
        user_msgs.append(user_msg)
        all_user_dialogue = "\n".join(f"用户提问：{m}" for m in user_msgs[-10:])
        portrait_context = (
            f"专业：{full_profile.get('major', '未填写')}，"
            f"课程：{full_profile.get('course', '未填写')}，"
            f"学习目标：{full_profile.get('study_goal', '未填写')}，"
            f"知识基础：{full_profile.get('knowledge_level', '中等')}"
        )
        portrait_result = await extract_portrait_prompt(all_user_dialogue, portrait_context)
        # 提取VARK学习风格（最近3组对话 + 历史VARK上下文）
        recent_user_history = "\n".join(f"用户提问：{m}" for m in user_msgs[-3:])
        raw_json = full_profile.get("raw_json") or {}
        vark_history = raw_json.get("vark_history", [])
        vark_context = ""
        if vark_history:
            last = vark_history[-1]
            vark_context = (
                f"上次VARK分析结果：视觉{int(last.get('V',0.25)*100)}%，"
                f"听觉{int(last.get('A',0.25)*100)}%，"
                f"读写{int(last.get('R',0.25)*100)}%，"
                f"动觉{int(last.get('K',0.25)*100)}%。"
                f"理由：{last.get('reason','')}"
            )
        vark_result = await extract_vark_prompt(recent_user_history, vark_context)
        portrait_result["vark_scores"] = {
            "V": vark_result.get("V_Score", 0.25),
            "A": vark_result.get("A_Score", 0.25),
            "R": vark_result.get("R_Score", 0.25),
            "K": vark_result.get("K_Score", 0.25),
            "trigger_words": vark_result.get("核心触发词", []),
            "reason": vark_result.get("判断理由", ""),
        }
        # 更新学生画像表
        update_user_profile(db=db, user_id=user_id_int, portrait_data=portrait_result)
        # 推送结束标识
        yield format_sse({"type": "done"})

        # 后台异步更新学习风格分析（不阻塞用户，在 done 之后执行）
        try:
            dialogue_lines = []
            for msg in history_messages[-30:]:
                role_label = "学生" if msg["role"] == "user" else "AI助手"
                dialogue_lines.append(f"{role_label}：{msg['content']}")
            dialogue_lines.append(f"学生：{user_msg}")
            if full_ai_reply:
                dialogue_lines.append(f"AI助手：{full_ai_reply}")
            full_dialogue = "\n".join(dialogue_lines)
            style_result = await extract_style_analysis(full_dialogue)
            if style_result:
                update_user_profile(db=db, user_id=user_id_int, portrait_data={"style_analysis": style_result})
        except Exception as style_err:
            logger.warning(f"学习风格分析更新失败: {style_err}")
    except Exception as e:
        logger.error(f"流式对话全局异常：{str(e)}")
        yield format_sse({"type": "error", "msg": f"对话服务异常：{str(e)}"})