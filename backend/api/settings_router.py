import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dotenv import load_dotenv, set_key

from api.common import get_current_user

router = APIRouter(prefix="/user", tags=["用户设置"])

ENV_PATH = "/app/.env"

class SettingsOut(BaseModel):
    llm_api_key: str        # masked: show first 4 + last 4 chars
    llm_base_url: str
    llm_model: str

class SettingsUpdate(BaseModel):
    llm_api_key: str
    llm_base_url: str
    llm_model: str

def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]

@router.get("/settings", response_model=SettingsOut)
def get_settings(current_user: int = Depends(get_current_user)):
    return SettingsOut(
        llm_api_key=_mask_key(os.getenv("LLM_API_KEY", "")),
        llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o"),
    )

@router.put("/settings")
def update_settings(settings: SettingsUpdate, current_user: int = Depends(get_current_user)):
    set_key(ENV_PATH, "LLM_API_KEY", settings.llm_api_key)
    set_key(ENV_PATH, "LLM_BASE_URL", settings.llm_base_url)
    set_key(ENV_PATH, "LLM_MODEL", settings.llm_model)
    # Update os.environ immediately for current process
    os.environ["LLM_API_KEY"] = settings.llm_api_key
    os.environ["LLM_BASE_URL"] = settings.llm_base_url
    os.environ["LLM_MODEL"] = settings.llm_model
    load_dotenv(ENV_PATH, override=True)
    return {"code": 200, "msg": "设置已更新", "data": {"llm_api_key": _mask_key(settings.llm_api_key), "llm_base_url": settings.llm_base_url, "llm_model": settings.llm_model}}
