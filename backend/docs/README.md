# EduAgent 后端文档

> 后端服务：基于 FastAPI + LangGraph 的个性化学习多智能体系统

---

## 目录

1. [技术栈](#1-技术栈)
2. [目录结构](#2-目录结构)
3. [核心架构](#3-核心架构)
4. [数据库模型](#4-数据库模型)
5. [智能体工作流](#5-智能体工作流)
6. [API 路由](#6-api-路由)
7. [配置说明](#7-配置说明)
8. [启动方式](#8-启动方式)

---

## 1. 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.100+ | Web 框架 |
| Uvicorn | 0.23+ | ASGI 服务器 |
| LangGraph | 0.2+ | 多智能体工作流 |
| LangChain | 0.3+ | LLM 工具链 |
| FAISS | 1.7+ | 向量数据库 |
| SQLAlchemy | 1.4+ | ORM |
| SQLite | - | 关系数据库 |
| JWT | 2.8+ | 身份认证 |
| BCrypt | 3.2+ | 密码加密 |

---

## 2. 目录结构

```
backend/
├── api/                    # API 路由（控制器层）
│   ├── v1/                 # 版本化 API
│   │   └── chat_stream_router.py    # SSE 流式对话接口
│   ├── user.py             # 用户管理接口（登录、注册）
│   ├── portrait_router.py  # 用户画像接口
│   ├── conversation_router.py       # 对话管理接口
│   ├── learning_path_router.py      # 学习路径接口
│   ├── resources_router.py # 学习资源接口
│   ├── settings_router.py  # 系统设置接口
│   └── common.py           # 公共依赖（如登录验证）
├── database/               # 数据库层
│   ├── connect.py          # 数据库连接、会话管理
│   ├── models.py           # SQLAlchemy 数据模型
│   ├── crud.py             # 通用 CRUD 操作
│   ├── crud_conversation.py        # 对话相关 CRUD
│   ├── crud_learning_path.py       # 学习路径 CRUD
│   └── crud_profile.py     # 用户画像 CRUD
├── services/               # 业务服务层
│   ├── llm_client.py       # LLM 客户端封装
│   ├── llm_agent.py        # LLM 智能体助手
│   ├── llm_utils.py        # LLM 工具函数
│   └── stream_service.py   # 流式服务
├── rag/                    # RAG（检索增强生成）模块
│   ├── document_loader.py  # 文档加载器
│   ├── embeddings.py       # 文本向量化
│   └── vector_store.py     # 向量存储管理
├── prompt/                 # 提示词模板
│   ├── manager.py          # 模板管理器
│   ├── prompt_templates.json       # 模板定义（JSON）
│   └── prompt_templates.md # 模板文档
├── agents/                 # 智能体节点（LangGraph）
│   └── agents.py           # 5个智能体定义
├── schemas/                # Pydantic 数据模型
│   ├── base.py             # 基础模型
│   ├── chat_schema.py      # 对话相关模型
│   ├── conversation_schema.py      # 会话模型
│   └── portrait_schema.py  # 用户画像模型
├── scripts/                # 脚本工具
│   ├── seed_db.py          # 数据库初始化
│   ├── data_init.py        # 数据初始化
│   └── rebuild_faiss.py    # 重建 FAISS 索引
├── utils/                  # 工具函数
│   ├── logger.py           # 日志配置
│   ├── exception.py        # 异常处理
│   └── response.py         # 统一响应格式
├── sql/                    # SQL 脚本
│   └── init.sql            # 数据库初始化脚本
├── alembic/                # 数据库迁移工具
├── main.py                 # 应用入口
├── workflow.py             # LangGraph 工作流定义
├── models_agent.py         # 智能体状态模型
└── requirements.txt        # Python 依赖
```

---

## 3. 核心架构

### 3.1 请求处理流程

```
客户端请求 → FastAPI 路由 → 依赖注入(认证) → 业务逻辑 → 数据库操作 → 返回响应
                  ↓
            异常处理中间件
```

### 3.2 分层架构

| 层级 | 文件位置 | 职责 |
|------|----------|------|
| 路由层 | `api/` | 接收请求、参数校验、调用服务 |
| 服务层 | `services/` | 业务逻辑、LLM 调用 |
| 数据层 | `database/` | 数据库操作、CRUD |
| 模型层 | `schemas/` | 数据结构定义、验证 |
| 工具层 | `utils/` | 通用工具、日志、异常 |

---

## 4. 数据库模型

### 4.1 核心表结构

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| `edu_user` | 用户表 | id, username, password, nickname, major |
| `edu_chat` | 对话记录表 | id, user_id, session_id, content, role |
| `students` | 学生画像表 | id, name, major, course, study_goal, weak_knowledge, learning_preference |
| `learning_records` | 学习记录表 | id, user_id, course, score, duration_minutes, study_date |
| `learning_path` | 学习路径表 | id, user_id, goal, steps(JSON), created_at |
| `conversation` | 会话表 | id, user_id, session_id, role, content, portrait_json |
| `edu_resource` | 资源存储表 | id, user_id, resource_type, content, progress |

### 4.2 模型关系

```
edu_user (1) ──── (*) edu_chat
edu_user (1) ──── (*) students
edu_user (1) ──── (*) learning_records
edu_user (1) ──── (*) learning_path
edu_user (1) ──── (*) conversation
```

---

## 5. 智能体工作流

### 5.1 LangGraph 工作流

系统使用 LangGraph 构建了一个多智能体协作管道，包含 5 个智能体节点：

```
profile → rag → generator → guardrail → planner → END
                     ↑                   │
                     └───────────────────┘
                    (条件循环，最多重试3次)
```

### 5.2 智能体说明

| 智能体 | 职责 | 输入 | 输出 |
|--------|------|------|------|
| `profile_agent` | 用户画像分析 | 用户ID | 用户画像数据 |
| `rag_agent` | 检索增强生成 | 画像 + 用户问题 | 相关文档片段 |
| `generator_agent` | 内容生成 | 文档 + 问题 | 学习资源（练习、笔记等） |
| `guardrail_agent` | 内容审核 | 生成内容 | 是否通过审核 |
| `planner_agent` | 学习路径规划 | 通过的内容 | 个性化学习路径 |

### 5.3 状态模型

智能体共享一个状态对象 `AgentState`，包含以下字段：

```python
class AgentState(TypedDict):
    user_id: str              # 用户ID
    messages: List[dict]       # 对话消息
    profile: dict             # 用户画像
    retrieved_docs: List[dict] # RAG 检索的文档
    generated_resource: dict   # 生成的学习资源
    is_approved: bool          # 审核状态
    learning_path: List[dict]  # 学习路径
    retry_count: int           # 重试次数
```

---

## 6. API 路由

### 6.1 路由清单

| 路由前缀 | 文件 | 说明 |
|----------|------|------|
| `/user/` | `api/user.py` | 用户管理（注册、登录、信息） |
| `/portrait/` | `api/portrait_router.py` | 用户画像（获取、更新） |
| `/conversation/` | `api/conversation_router.py` | 对话管理（会话列表、消息） |
| `/agent/chat/stream` | `main.py` | SSE 流式对话 |
| `/learning-path/` | `api/learning_path_router.py` | 学习路径（列表、详情） |
| `/resources/` | `api/resources_router.py` | 学习资源（课程、文件） |
| `/settings/` | `api/settings_router.py` | 系统设置（用户配置） |
| `/docs` | FastAPI 自动生成 | API 文档 |

### 6.2 认证机制

使用 JWT (JSON Web Token) 进行身份认证：

```python
# 获取当前用户（依赖注入）
def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    # 验证 token，返回用户 ID
```

需要认证的接口通过 `Depends(get_current_user)` 注入用户信息。

---

## 7. 配置说明

### 7.1 环境变量

后端使用 `.env` 文件配置，关键配置项：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | LLM API 密钥 | 必填 |
| `LLM_BASE_URL` | LLM API 地址 | https://api.openai.com/v1 |
| `LLM_MODEL` | 使用的模型 | gpt-4o |
| `JWT_SECRET_KEY` | JWT 密钥 | 必填（至少32位） |
| `JWT_ALGORITHM` | JWT 算法 | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间 | 120 |
| `DATABASE_URL` | 数据库连接 | sqlite:///./edu_agent.db |

### 7.2 配置文件位置

- 开发环境：项目根目录 `.env`
- Docker 环境：通过 `docker-compose.yml` 挂载 `.env`

---

## 8. 启动方式

### 8.1 本地开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务（热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 8.2 Docker 部署

```bash
cd docker
docker compose up -d
```

### 8.3 数据库初始化

```bash
cd backend

# 初始化数据库（创建表、默认用户）
python scripts/seed_db.py

# 重建 FAISS 索引
python scripts/rebuild_faiss.py
```

### 8.4 访问 API 文档

启动后访问 `http://localhost:8000/docs` 查看交互式 API 文档。

---

## 附录：核心文件说明

### main.py

应用入口，负责：
- 加载环境变量
- 配置 CORS 中间件
- 注册路由
- 初始化数据库
- 定义 SSE 流式接口

### workflow.py

LangGraph 工作流定义，编译智能体图并提供 `create_workflow_graph()` 函数。

### services/llm_client.py

LLM 客户端封装，支持多种 LLM 提供商（OpenAI、DeepSeek 等），统一接口调用。