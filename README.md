# EduAgent

基于大模型的个性化资源生成与学习多智能体系统 — Docker 一键部署版

## 快速开始

```bash
# 1. 配置环境变量（填入你的 LLM API Key）
cp .env.example .env
# 编辑 .env，修改 JWT_SECRET_KEY 为随机字符串

# 2. 启动所有服务
docker compose up -d

# 3. 访问
# 前端: http://localhost
# 后端 Swagger: http://localhost:8000/docs
# 默认账号: admin / admin123
```

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | Python 3.11 / FastAPI / Uvicorn |
| AI 框架 | LangGraph + LangChain |
| 向量数据库 | FAISS |
| LLM | OpenAI 兼容接口（OpenCode / DeepSeek / OpenAI） |
| 前端 | Vue 3 + Vite + Element Plus |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 认证 | JWT HS256 + bcrypt |
| 容器化 | Docker + docker-compose + nginx |

## 项目结构

```
EduAgent/
├── backend/          # FastAPI 后端
│   ├── api/          # 路由 (user, conversation, portrait, agent)
│   ├── database/     # SQLAlchemy ORM + CRUD
│   ├── services/     # LLM 客户端 + SSE 流
│   ├── rag/          # 文档加载 + 向量化 + FAISS 检索
│   ├── agents.py     # 5 个 AI Agent
│   ├── workflow.py   # LangGraph 工作流
│   └── scripts/      # 种子数据 + FAISS 重建
├── frontend/         # Vue 3 前端
│   ├── src/views/    # 登录、AI对话、学习路径、资源等
│   ├── src/api/      # API 调用层
│   └── src/stores/   # Pinia 状态管理
├── data/             # 知识库数据 + FAISS 索引
├── docker/           # Dockerfile + compose + nginx 配置
├── scripts/          # 打包和启动脚本
└── .env.example      # 环境变量模板
```

## API 概览

| Method | Path | 说明 |
|--------|------|------|
| POST | /user/login | 用户登录 |
| POST | /user/register | 用户注册 |
| GET | /user/info | 当前用户信息 |
| POST | /api/v1/chat/stream | AI 对话（SSE 流） |
| POST | /agent/chat/stream | Agent 工作流对话 |
| GET | /portrait/me | 学习画像 |
| POST | /portrait/update | 更新画像 |
| GET | /conversation/session/list | 对话历史 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| LLM_API_KEY | LLM API 密钥 | — |
| LLM_BASE_URL | LLM 接口地址 | https://opencode.ai/zen/v1 |
| LLM_MODEL | 模型名称 | opencode-go/deepseek-v4-flash |
| DATABASE_URL | 数据库连接 | sqlite:///./edu_agent.db |
| JWT_SECRET_KEY | JWT 密钥（必填） | — |
| BACKEND_PORT | 后端端口 | 8000 |
| FRONTEND_PORT | 前端端口 | 80 |

## 分发部署

```bash
# 打包（在开发者机器上）
./scripts/package.sh          # Linux/Mac
# 或 pwsh scripts/package.ps1 # Windows

# 部署（在目标机器上）
tar -xzf eduagent-dist.tar.gz
cd eduagent-dist
./scripts/up.sh               # Linux/Mac
# 或 pwsh scripts/up.ps1      # Windows
```

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| student1 | 123456 | 学生 |

## 开发

```bash
# 后端开发
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # 编辑填入密钥
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端开发
cd frontend
npm install
npm run dev
```

## License

MIT
