# AI_Agent_System

基于大模型的个性化学习多智能体系统，提供智能对话、学习路径规划、资源管理等功能。

## 功能特性

- 🤖 **AI 智能对话**：支持流式响应的智能问答系统
- 📚 **学习路径规划**：根据用户画像生成个性化学习路径
- 👤 **用户学习画像**：追踪和分析用户学习行为
- ⚙️ **LLM 配置管理**：支持多种 OpenAI 兼容接口
- 📊 **管理后台**：用户管理和资源统计

## 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue | 3.5+ |
| UI 组件 | Element Plus | 2.14+ |
| 状态管理 | Pinia | 3.0+ |
| 路由 | Vue Router | 5.1+ |
| 后端框架 | FastAPI | 0.100+ |
| 智能体框架 | LangGraph | 0.2+ |
| 向量数据库 | FAISS | 1.7+ |
| 数据库 | SQLite | - |
| 容器化 | Docker | - |

## 快速开始

### 方式一：Docker 一键部署（推荐）

#### 1. 安装 Docker

**Windows / Mac：**
- 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- 安装并启动，等待右下角鲸鱼图标变绿

**Linux（Ubuntu/Debian）：**
```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo usermod -aG docker $USER
# 重新登录使权限生效
```

#### 2. 配置环境变量

```bash
# 进入项目目录
cd AI_Agent_System

# 复制环境变量模板
cp .env.example .env

# 编辑配置文件（Windows 用 notepad .env）
nano .env
```

修改 `.env` 文件中的关键配置：

```env
# AI 模型配置
LLM_API_KEY="sk-你的API密钥"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4o"

# JWT 密钥（必须修改，至少32位随机字符串）
JWT_SECRET_KEY="your-random-secret-key-here"
```

> **没有 API Key？**
> - DeepSeek：[platform.deepseek.com](https://platform.deepseek.com)
> - OpenAI：[platform.openai.com](https://platform.openai.com)
> - 其他兼容服务：修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可

#### 3. 启动服务

```bash
docker compose up -d
```

首次启动会自动下载依赖，约 2-3 分钟。查看启动状态：

```bash
# 查看所有容器状态
docker compose ps

# 查看后端日志
docker compose logs backend --tail=20
```

看到 `Uvicorn running on http://0.0.0.0:8000` 表示启动成功。

#### 4. 访问服务

| 地址 | 说明 |
|------|------|
| http://localhost | 前端页面 |
| http://localhost:8000/docs | API 文档 |

#### 演示账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |
| `student1` | `123456` | 学生 |

### 方式二：本地开发

#### 后端开发

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 配置 LLM_API_KEY 和 JWT_SECRET_KEY

# 初始化数据库
python -m alembic upgrade head
python scripts/seed_db.py

# 启动开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
# 进入前端目录
cd frontend

# 安装依赖（需要 Node.js >= 22）
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看前端页面。

## 目录结构

```
AI_Agent_System/
├── backend/                    # 后端代码
│   ├── api/                    # API 路由
│   │   ├── v1/                 # v1 版本 API
│   │   ├── user.py             # 用户相关接口
│   │   ├── conversation_router.py  # 对话接口
│   │   ├── portrait_router.py  # 学习画像接口
│   │   └── settings_router.py  # 设置接口
│   ├── database/               # 数据库操作
│   ├── services/               # 业务服务
│   ├── rag/                    # RAG 相关
│   ├── prompt/                 # 提示词模板
│   ├── schemas/                # 数据模型
│   ├── utils/                  # 工具函数
│   ├── main.py                 # 入口文件
│   └── requirements.txt        # 依赖列表
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── components/         # 公共组件
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── views/              # 页面视图
│   │   └── router/             # 路由配置
│   ├── index.html
│   └── package.json
├── .env.example               # 环境变量模板
├── docker-compose.yml         # Docker 配置
└── README.md                  # 项目说明
```

## 常用命令

```bash
# Docker 命令
docker compose up -d          # 启动服务
docker compose down           # 停止服务
docker compose logs backend   # 查看后端日志
docker compose restart        # 重启服务

# 后端命令
uvicorn main:app --reload     # 启动开发服务器
alembic revision --autogenerate -m "描述"  # 创建迁移
alembic upgrade head          # 执行迁移

# 前端命令
npm run dev                   # 启动开发服务器
npm run build                 # 构建生产版本
npm run format                # 格式化代码
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/user/login` | POST | 用户登录 |
| `/user/register` | POST | 用户注册 |
| `/user/info` | GET | 获取用户信息 |
| `/api/v1/chat/stream` | POST | AI 对话（流式） |
| `/portrait/me` | GET | 获取学习画像 |
| `/portrait/update` | POST | 更新学习画像 |
| `/user/settings` | GET/PUT | 用户设置 |

完整 API 文档：http://localhost:8000/docs

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | LLM API 密钥 | - |
| `LLM_BASE_URL` | LLM API 地址 | https://api.openai.com/v1 |
| `LLM_MODEL` | LLM 模型名称 | gpt-4o |
| `JWT_SECRET_KEY` | JWT 密钥（必改） | - |
| `BACKEND_PORT` | 后端端口 | 8000 |
| `FRONTEND_PORT` | 前端端口 | 80 |

## 常见问题

### Q：启动后无法访问？
A：检查 Docker 是否运行，查看日志：
```bash
docker compose ps
docker compose logs backend
```

### Q：AI 聊天无响应？
A：检查 `.env` 中的 `LLM_API_KEY` 是否正确配置。

### Q：端口被占用？
A：修改 `.env` 中的端口号：
```env
BACKEND_PORT=8080
FRONTEND_PORT=8081
```

### Q：JWT_SECRET_KEY 错误？
A：`.env` 中的 `JWT_SECRET_KEY` 不能以 `change-` 开头，需要设置为至少 32 位的随机字符串。

## 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交修改：`git commit -m 'Add xxx'`
4. 推送到分支：`git push origin feature/xxx`
5. 提交 Pull Request

## License

MIT License