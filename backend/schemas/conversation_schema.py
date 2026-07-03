from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# 创建单条对话接收参数
class ConversationCreate(BaseModel):
    session_id: str
    role: str = Field(pattern=r"^(user|assistant)$", description="仅允许user/assistant")
    content: str

# 单条对话返回结构
class ConversationItem(ConversationCreate):
    id: int
    portrait_json: Optional[dict]
    create_time: str

# 分页查询对话返回体
class ConversationPageResp(BaseModel):
    total: int
    page: int
    page_size: int
    list: List[ConversationItem]

class SessionListResp(BaseModel):
    session_ids: List[str]