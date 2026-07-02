from dotenv import load_dotenv
load_dotenv()

import json
import sys
import os

# Ensure project root is on sys.path so local `api` package imports work
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from api.portrait_router import router as portrait_router
from api.conversation_router import router as conv_router
from api.v1.chat_stream_router import router as chat_stream_router
from api.resources_router import router as resources_router
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from database.connect import engine, Base, ensure_default_user
from api import user
from api.common import get_current_user
from utils.exception import register_exception
from utils.logger import log

# Agent workflow (LangGraph)
from backend.workflow import create_workflow_graph
from backend.models_agent import AgentState

Base.metadata.create_all(bind=engine)
ensure_default_user()

app = FastAPI(title="教育助手后端")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev
        "http://localhost:5174",  # Vite alternate port
        "http://localhost:5175",  # Vite alternate port
        "http://localhost:5176",  # Vite alternate port
        "http://localhost",        # Docker nginx proxy
        "http://127.0.0.1:5173",   # Alternative dev
        "http://127.0.0.1:5174",   # Alternative dev alternate port
        "http://127.0.0.1:5175",   # Alternative dev alternate port
        "http://127.0.0.1:5176",   # Alternative dev alternate port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常
register_exception(app)

# 路由
app.include_router(user.router)
app.include_router(conv_router)
# 注册用户画像模块接口
app.include_router(portrait_router)
app.include_router(chat_stream_router)
from api.settings_router import router as settings_router
app.include_router(settings_router)
app.include_router(resources_router)

@app.get("/")
def root():
    return {"msg": "服务正常，访问 /docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agent/chat/stream")
async def agent_chat_stream(request: dict, current_user: int = Depends(get_current_user)):
    """SSE streaming endpoint for the AI agent workflow.

    Drives the full ``profile -> rag -> generator -> guardrail -> planner``
    pipeline and streams LangGraph events to the client as Server-Sent Events.
    """
    async def event_stream():
        graph = create_workflow_graph()
        state = AgentState(
            user_id=str(current_user),
            messages=[{"role": "user", "content": request.get("message", "")}],
            profile={}, retrieved_docs=[], generated_resource={},
            is_approved=False, learning_path=[], retry_count=0
        )
        try:
            for event in graph.stream(state):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"data: {json.dumps({'error': str(exc)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)