"""Profile / utility helpers backed by the unified LLMClient.

All transport goes through `services.llm_client.LLMClient`.  There is no
provider-specific code in this file.
"""
import json
import logging
from services.llm_client import LLMClient

logger = logging.getLogger(__name__)


PROFILE_PROMPT = """你是一位专业的教育心理学专家，擅长分析学生的学习特征。

请根据以下学生的对话内容，输出一份严格的JSON格式学生画像（不要带任何其他废话，只输出JSON）。

维度定义：
1. knowledge_base (知识基础): 初学者/基础薄弱/中等/良好/优秀
2. cognitive_style (认知风格): 视觉型/听觉型/动觉型/读写型/混合型
3. weak_points (易错点): 具体的薄弱知识点，用逗号分隔
4. interest (兴趣): 感兴趣的学科或领域，用逗号分隔
5. learning_pace (学习节奏): 快速/中等/慢速/时快时慢
6. emotional_state (情绪状态): 积极/中性/焦虑/疲惫/抵触

学生对话：
{dialogue}

输出格式（严格JSON，无其他内容）：
{{"knowledge_base": "...", "cognitive_style": "...", "weak_points": "...", "interest": "...", "learning_pace": "...", "emotional_state": "..."}}"""


def extract_profile(dialogue: str) -> dict | None:
    """Run the profile prompt through LLMClient and parse JSON output."""
    prompt = PROFILE_PROMPT.format(dialogue=dialogue)
    client = LLMClient()
    response = client.chat_text([{"role": "user", "content": prompt}])

    if response is None:
        return None

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        logger.warning("JSON 解析失败，原始响应: %s", response[:200])
        return None


def get_default_profile() -> dict:
    return {
        "knowledge_base": "初学者",
        "cognitive_style": "视觉型",
        "weak_points": "数学推导,逻辑推理",
        "interest": "人工智能,机器学习,编程",
        "learning_pace": "中等",
        "emotional_state": "积极",
    }
