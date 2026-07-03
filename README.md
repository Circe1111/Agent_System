# EduAgent

基于大模型的个性化学习多智能体系统 —— 支持 Docker 容器化部署和本地直接启动，无需复杂配置。

---

## 项目架构

```
EduAgent/
├── backend/                 # 后端服务（FastAPI + LangGraph）
├── frontend/               # 前端应用（Vue 3 + Element Plus）
├── docker/                 # Docker 配置文件
├── data/                   # 知识库数据和初始化数据
├── docs/                   # 项目文档（新增）
│   └── API.md              # API 接口文档
├── 测试文档/                # 测试文档和脚本
└── README.md               # 项目说明文档
```

---

## 快速开始

### 方式一：Docker 容器化启动（推荐，约 5 分钟）

#### 1. 安装 Docker

**Windows 用户：**
1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. 双击安装，一路点"下一步"
3. 安装完成后启动 Docker Desktop，等待右下角图标变绿（**白色鲸鱼图标**）
4. 打开 PowerShell（开始菜单 → 搜索 "PowerShell" → 打开）
5. 输入 `docker --version`，看到版本号就说明安装成功

**Mac 用户：**
同上，下载安装 Docker Desktop 即可。

**Linux 用户（Ubuntu/Debian）：**
```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo usermod -aG docker $USER
sudo service docker start
docker --version
```

#### 2. 配置 API Key

```bash
cd EduAgent
cp .env.example .env
notepad .env
```

修改以下配置：
```env
LLM_API_KEY="sk-你的API密钥"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4o"
JWT_SECRET_KEY="aB3xK9mQ7wR2tY5nL8pV1cF4hJ6dS0gU"
```

> ❓ **没有 API Key？**
> - **DeepSeek**：去 [platform.deepseek.com](https://platform.deepseek.com) 注册 → 创建 API Key
> - **OpenAI**：去 [platform.openai.com](https://platform.openai.com) 获取
> - **其他兼容服务**：修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可

#### 3. 一键启动

```bash
cd docker
docker compose up -d
```

首次启动会自动下载镜像、安装依赖、创建数据库，**大约等 2-3 分钟**。

#### 4. 访问系统

| 地址 | 说明 |
|------|------|
| http://localhost | 🔥 **前端页面**（主要使用） |
| http://localhost:8000/docs | 后端 API 文档 |

---

### 方式二：本地直接启动（开发调试）

#### 1. 环境准备

**Python 环境（后端）：**
```bash
# 确保安装 Python 3.11+
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# 安装后端依赖
cd backend
pip install -r requirements.txt
```

**Node.js 环境（前端）：**
```bash
# 确保安装 Node.js 22+
node --version

# 安装前端依赖
cd frontend
npm install
```

#### 2. 配置环境变量

```bash
cp .env.example .env
notepad .env
```

修改配置（参考方式一）。

#### 3. 启动服务

**启动后端（终端 1）：**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端（终端 2）：**
```bash
cd frontend
npm run dev
```

#### 4. 访问系统

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 🔥 **前端页面**（开发模式） |
| http://localhost:8000/docs | 后端 API 文档 |

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [后端文档](backend/docs/README.md) | 后端技术栈、目录结构、核心逻辑 |
| [前端文档](frontend/docs/README.md) | 前端技术栈、目录结构、组件说明 |
| [API 文档](docs/API.md) | 接口说明、使用示例 |
| [本地开发测试指南](测试文档/本地开发测试指南.md) | 详细的开发和测试流程 |
| [项目测试说明](测试文档/项目测试说明.md) | 测试用例、测试报告、截图说明 |

---

## 常用命令

### Docker 部署

```bash
# 启动服务
cd docker
docker compose up -d

# 查看后端日志
docker compose logs backend

# 查看所有容器状态
docker compose ps

# 停止服务（数据保留）
docker compose down

# 重新构建并启动
docker compose up -d --build

# 完全重置（删除所有数据，慎用！）
docker compose down -v
```

### 本地开发

```bash
# 后端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npm run dev

# 前端构建
npm run build

# 前端格式化
npm run format
```

---

## 环境变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `LLM_API_KEY` | API 密钥（**必填**） | sk-xxxx |
| `LLM_BASE_URL` | API 接口地址 | https://api.openai.com/v1 |
| `LLM_MODEL` | 模型名称 | gpt-4o |
| `JWT_SECRET_KEY` | JWT 密钥（**必改**，不能以 `change-` 开头） | aB3xK9mQ... |
| `BACKEND_PORT` | 后端端口（默认 8000） | 8000 |
| `FRONTEND_PORT` | 前端端口（默认 80） | 80 |

---

## 常见问题

### Q：启动后 http://localhost 打不开？

**A：** 首次启动需要 2-3 分钟初始化，等一会儿再刷新。如果还是不行：
```bash
docker compose ps
docker compose logs backend
```

### Q：登录提示"账号密码错误"？

**A：** 确认使用的是正确的演示账号：
- 管理员：`admin` / `admin123`
- 学生：`student1` / `123456`

### Q：AI 聊天没有回复？

**A：** 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确填写：
```bash
docker compose logs backend | grep ERROR
```

### Q：Docker 提示"端口被占用"？

**A：** 修改 `.env` 中的端口号：
```env
BACKEND_PORT=8080
FRONTEND_PORT=8081
```
然后重新启动：`docker compose up -d`

### Q：本地开发时前端无法连接后端？

**A：** 检查后端服务是否启动，确认端口为 8000。如果前端报 CORS 错误，检查 `main.py` 中的 CORS 配置。

---

## 技术栈

| 分类 | 技术 |
|------|------|
| 后端框架 | Python 3.11 / FastAPI |
| AI 框架 | LangGraph / LangChain |
| 向量数据库 | FAISS |
| 数据库 | SQLite |
| 认证 | JWT / BCrypt |
| 前端框架 | Vue 3 / Vite |
| UI 组件 | Element Plus |
| 状态管理 | Pinia |
| 容器化 | Docker / Docker Compose |
| 代理 | Nginx |

---

## License

MIT