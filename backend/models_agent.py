from typing import List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated

class AgentState(TypedDict):
    user_id: str
    messages: Annotated[List[Dict[str, str]], add_messages]
    profile: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    generated_resource: Dict[str, str]
    is_approved: bool
    learning_path: List[Dict[str, str]]
    retry_count: int