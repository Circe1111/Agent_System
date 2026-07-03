"""Profile / utility helpers backed by the unified LLMClient.

All transport goes through `services.llm_client.LLMClient`.  There is no
provider-specific code in this file.
"""
import json
import logging
import re
from services.llm_client import LLMClient

logger = logging.getLogger(__name__)


def _clean_json_response(response: str) -> str:
    """Strip markdown code blocks and extract pure JSON from LLM response."""
    if not response:
        return response
    text = response.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    # Try to extract JSON from text (LLM often adds preamble like "好的，以下是分析结果：")
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]
    return text.strip()


PROFILE_PROMPT = """你是一位专业的教育心理学专家，擅长分析学生的学习特征。

请根据以下学生的学习提问内容，输出一份严格的JSON格式学生画像（不要带任何其他废话，只输出JSON）。
注意：只分析【用户提问】的内容，不要分析AI助手的回答。从学生的提问中推断其知识薄弱点和兴趣方向。

学生背景信息：
__CONTEXT__

维度定义：
1. knowledge_base (知识基础): 初学者/基础薄弱/中等/良好/优秀
2. cognitive_style (认知风格): 视觉型/听觉型/动觉型/读写型/混合型
3. weak_points (易错点): 学生提问涉及的具体知识点名称。学生对某个主题提出疑问，就说明该主题是其薄弱/不熟悉的知识点，必须提取为 weak_points。例如问"Python基本函数有哪些"则 weak_points 应包含"Python基础函数"；问"DFA是什么意思"则包含"DFA与自动机"。每条提问至少提取 1 个 weak_point，用逗号分隔
4. interest (兴趣): 学生提问涉及的学科或领域，用逗号分隔
5. learning_pace (学习节奏): 快速/中等/慢速/时快时慢
6. emotional_state (情绪状态): 积极/中性/焦虑/疲惫/抵触

学生提问记录：
__DIALOGUE__

输出格式（严格JSON，无其他内容）：
{"knowledge_base": "...", "cognitive_style": "...", "weak_points": "...", "interest": "...", "learning_pace": "...", "emotional_state": "..."}"""


def extract_profile(dialogue: str, context: str = "") -> dict | None:
    """Run the profile prompt through LLMClient and parse JSON output."""
    prompt = PROFILE_PROMPT.replace("__CONTEXT__", context or "暂无学生背景信息").replace("__DIALOGUE__", dialogue)
    client = LLMClient()
    response = client.chat_text([{"role": "user", "content": prompt}])

    if response is None:
        return None

    cleaned = _clean_json_response(response)
    try:
        return json.loads(cleaned)
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


VARK_PROMPT = """你是一位教育心理学VARK分析专家，擅长通过语言特征精准识别学习者的感知偏好。

请严格遵循以下规则分析用户最近的提问，输出其VARK（视觉型/听觉型/读写型/动觉型）学习风格的四维概率分布。

【分析规则（思维链）】
1. 动词扫描：提取谓语动词（看/见/描绘/展示/画/图=视觉V；听/讲/聊/叙述/说/解释=听觉A；写/记/总结/列/定义/读/文档=读写R；做/操作/试/跑/摸索/实践/练习/动手=动觉K）。
2. 名词扫描：提取请求的目标对象（图/表/框架/色/可视化/示意图=视觉；音频/节奏/语调/视频/讲座=听觉；书单/原文/清单/笔记/文档=读写；步骤/案例/工具/实战/项目/代码=动觉）。
3. 否定纠偏：检测"别"、"不要"、"不用"等词，对应维度权重强制降低至0.1以下。
4. 混合加权：允许输出混合概率（因为现实中极少有人是100%纯血型），四项分数之和需等于1。

【上次VARK分析结果（参考）】
__CONTEXT__

【输出格式（强制遵守）】
请务必只输出以下JSON，不要带任何其他文字：
{"V_Score":0.0, "A_Score":0.0, "R_Score":0.0, "K_Score":0.0, "核心触发词":["词1","词2"], "判断理由":"一句话解释"}

【重要约束】
如果用户输入没有表达任何学习意图（如闲聊天气、日常问候），请直接输出均匀分布：
{"V_Score":0.25, "A_Score":0.25, "R_Score":0.25, "K_Score":0.25, "核心触发词":[], "判断理由":"无学习意图，均匀分布"}

用户最近提问：
__DIALOGUE__"""


def extract_vark(dialogue: str, context: str = "") -> dict | None:
    """Run the VARK prompt through LLMClient and parse JSON output."""
    prompt = VARK_PROMPT.replace("__CONTEXT__", context or "暂无历史VARK数据").replace("__DIALOGUE__", dialogue)
    client = LLMClient()
    response = client.chat_text([{"role": "user", "content": prompt}])

    if response is None:
        return None

    cleaned = _clean_json_response(response)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("VARK JSON 解析失败，原始响应: %s", response[:200])
        return None


def get_default_vark() -> dict:
    return {
        "V_Score": 0.25,
        "A_Score": 0.25,
        "R_Score": 0.25,
        "K_Score": 0.25,
        "核心触发词": [],
        "判断理由": "暂无足够数据",
    }


def _salvage_truncated_json(text: str) -> dict | None:
    """Try to repair a truncated JSON by closing open brackets/strings."""
    if not text:
        return None
    text = text.strip()
    if not text.startswith('{'):
        return None

    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')
    in_string = text.count('"') % 2 != 0

    if in_string:
        text += '"'
    for _ in range(open_brackets):
        text += ']'
    for _ in range(open_braces):
        text += '}'

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


LEARNING_STYLE_ANALYSIS_PROMPT = """你是一位资深的教育心理学与学习科学专家。请根据以下学生与AI助手的对话历史，分析该学生的学习风格。

【重要规则——必须严格遵守】
1. 不要随意输出"混合型"！只有当四种风格关键词出现频率确实非常均衡时，才允许输出混合型。
2. 仔细扫描对话中的关键词，只要有任一风格的关键词明显多于其他风格，就输出该风格。
3. 如果有多个风格出现，选关键词出现最多、表述最强烈的那个作为主导风格。

【关键词对照表——用于判断学习风格】
- 视觉型：看到、看图、图表、图示、图解、视频、演示、可视化、展示、看看、观察、画、颜色、图形、画面、PPT、幻灯片、思维导图、流程图
- 听觉型：听到、听听、讲解、说、讲、声音、音频、讨论、对话、聊、问、回答、口头、朗读、录音、播客、听书
- 读写型：阅读、写、笔记、文字、文章、书、文献、资料、记录、总结、整理、归纳、列表、清单、教材、课本、文档
- 动觉型：感觉、感受、体验、动手、试试、尝试、实践、操作、模拟、实验、做、练习、演练、触摸、动手做、身体、动作、活动、参与、亲身体验、实操、演练、动手实践

【分析步骤】
1. 逐条扫描对话，统计每种风格关键词的出现次数
2. 选出出现次数最多的风格作为主导风格
3. 如果两种风格关键词数量接近，选择表述更强烈、更主动的那个
4. 只有当四种风格关键词数量确实非常接近（差异不超过1个），才输出"混合型"

【对话历史】
__DIALOGUE__

【输出格式（严格JSON，无其他内容）】
{
  "cognitive_style": "视觉型/听觉型/读写型/动觉型/混合型",
  "style_label": "视觉型学习者/听觉型学习者/读写型学习者/动觉型学习者/混合型学习者",
  "confidence": 0.85,
  "style_description": "对该风格特征的详细描述，必须引用对话中的具体用词作为证据（100-150字）",
  "strengths": ["优势1", "优势2", "优势3"],
  "weaknesses": ["不足1", "不足2"],
  "study_tips": [
    {"tip": "具体建议1", "detail": "详细说明1"},
    {"tip": "具体建议2", "detail": "详细说明2"},
    {"tip": "具体建议3", "detail": "详细说明3"}
  ],
  "recommended_tools": ["推荐工具1", "推荐工具2"],
  "analysis_summary": "整体分析总结，必须说明是基于哪些关键词得出的判断（50-80字）"
}"""


def analyze_learning_style_from_history(dialogue: str) -> dict | None:
    """Analyze user's learning style based on conversation history."""
    prompt = LEARNING_STYLE_ANALYSIS_PROMPT.replace("__DIALOGUE__", dialogue)
    client = LLMClient()
    response = client.chat_text(
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    if response is None:
        logger.warning("学习风格分析 LLM 返回 None")
        return None

    logger.info("学习风格分析 LLM 原始响应: %s", response[:300])
    cleaned = _clean_json_response(response)
    try:
        result = json.loads(cleaned)
        logger.info("学习风格分析结果: %s (置信度: %s)", result.get("cognitive_style"), result.get("confidence"))
        return result
    except json.JSONDecodeError:
        logger.warning("学习风格分析 JSON 解析失败，原始响应: %s", response[:300])
        salvaged = _salvage_truncated_json(cleaned)
        if salvaged:
            logger.info("学习风格分析 JSON 修复成功")
            return salvaged
        return None


def get_default_style_analysis() -> dict:
    return {
        "cognitive_style": "混合型",
        "style_label": "混合型学习者",
        "confidence": 0.5,
        "style_description": "暂未积累足够的对话数据来进行精准的学习风格分析。请多与AI助手互动，系统将逐步了解您的学习偏好。",
        "strengths": ["适应性强", "灵活多变"],
        "weaknesses": ["风格尚未明确"],
        "study_tips": [
            {"tip": "多与AI助手交流", "detail": "通过提问和讨论，让系统更好地了解你的学习习惯和偏好。"},
            {"tip": "尝试不同学习方式", "detail": "在学习过程中尝试图表、音频、文字笔记、动手实践等多种方式，找到最适合自己的。"},
        ],
        "recommended_tools": ["思维导图", "在线笔记"],
        "analysis_summary": "当前对话数据不足，建议多与AI互动以获得更精准的学习风格分析。",
    }