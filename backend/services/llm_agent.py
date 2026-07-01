import os
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self, provider="xunfei"):
        self.provider = provider
        self.config = self._load_config()
    
    def _load_config(self):
        config = {}
        if self.provider == "xunfei":
            config["api_key"] = os.getenv("SPARK_API_KEY")
            config["api_secret"] = os.getenv("SPARK_API_SECRET")
            config["model"] = os.getenv("SPARK_MODEL", "spark-x2")
            config["base_url"] = os.getenv("SPARK_BASE_URL", "https://spark-api-open.xf-yun.com/x2/chat/completions")
        elif self.provider == "deepseek":
            config["api_key"] = os.getenv("DEEPSEEK_API_KEY")
            config["model"] = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            config["base_url"] = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions")
        return config
    
    def call(self, messages, temperature=0.7, max_tokens=4096):
        if self.provider == "xunfei":
            return self._call_xunfei(messages, temperature, max_tokens)
        elif self.provider == "deepseek":
            return self._call_deepseek(messages, temperature, max_tokens)
        else:
            raise ValueError(f"不支持的provider: {self.provider}")
    
    def _call_xunfei(self, messages, temperature, max_tokens):
        auth_string = f"{self.config['api_key']}:{self.config['api_secret']}"
        encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {encoded_auth}"
        }
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        try:
            response = requests.post(self.config["base_url"], json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f">>> 讯飞API错误 (HTTP {response.status_code}): {response.text}")
                return None
        except Exception as e:
            print(f">>> 讯飞请求异常: {e}")
            return None
    
    def _call_deepseek(self, messages, temperature, max_tokens):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config['api_key']}"
        }
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        try:
            response = requests.post(self.config["base_url"], json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f">>> DeepSeek API错误 (HTTP {response.status_code}): {response.text}")
                return None
        except Exception as e:
            print(f">>> DeepSeek请求异常: {e}")
            return None


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
{"knowledge_base": "...", "cognitive_style": "...", "weak_points": "...", "interest": "...", "learning_pace": "...", "emotional_state": "..."}"""


def extract_profile(dialogue):
    prompt = PROFILE_PROMPT.format(dialogue=dialogue)
    client = LLMClient()
    response = client.call([{"role": "user", "content": prompt}])
    
    if response is None:
        return None
    
    try:
        profile = json.loads(response)
        return profile
    except json.JSONDecodeError:
        print(f">>> JSON解析失败，原始响应: {response[:200]}")
        return None


def get_default_profile():
    return {
        "knowledge_base": "初学者",
        "cognitive_style": "视觉型",
        "weak_points": "数学推导,逻辑推理",
        "interest": "人工智能,机器学习,编程",
        "learning_pace": "中等",
        "emotional_state": "积极"
    }