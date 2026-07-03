# EduAgent

基于大模型的个性化学习多智能体系统 —— 支持 Docker 容器化部署和本地直接启动，无需复杂配置。

***

## 项目架构

```
EduAgent/
├── backend/                 # 后端服务（FastAPI + LangGraph）
├── frontend/               # 前端应用（Vue 3 + Element Plus）
├── docker/                 # Docker 配置文件
├── data/                   # 知识库数据和初始化数据
├── docs/                   # 项目文档
│   └── API.md              # API 接口文档
├── 测试文档/                # 测试文档和脚本
└── README.md               # 项目说明文档
```

***

## 项目启动指南

### 一、初次启动项目的完整操作流程

首次启动项目需要完成环境准备、依赖安装和配置等步骤，以下是完整的操作流程：

#### 1.1 环境准备

**检查并安装 Python（后端）：**

```powershell
# 检查 Python 版本，需为 3.11+
python --version
```

如果未安装或版本低于 3.11，请前往 [Python 官网](https://www.python.org/downloads/) 下载并安装。

**检查并安装 Node.js（前端）：**

```powershell
# 检查 Node.js 版本，需为 22+
node --version
```

如果未安装或版本低于 22，请前往 [Node.js 官网](https://nodejs.org/) 下载并安装。

#### 1.2 创建虚拟环境

```powershell
# 进入项目根目录
cd EduAgent

# 创建 Python 虚拟环境
python -m venv venv
```

#### 1.3 激活虚拟环境 

<br />

```powershell
# Windows PowerShell 用户（推荐）
.\venv\Scripts\Activate.ps1

# Windows CMD 用户
.\venv\Scripts\activate.bat

# Mac/Linux 用户
source venv/bin/activate
```

> **注意事项：**
>
> - 激活成功后，终端提示符前会显示 `(venv)` 标识
> - 如果 PowerShell 执行脚本时报错，请参考下方"四、虚拟环境激活详细指南"

#### 1.4 安装后端依赖

```powershell
# 进入后端目录
cd backend

# 安装依赖（约 2-5 分钟，取决于网络速度）
pip install -r requirements.txt
```

#### 1.5 安装前端依赖

```powershell
# 进入前端目录
cd frontend

# 安装依赖（约 1-3 分钟）
npm install
```

#### 1.6 配置环境变量

```powershell
# 返回项目根目录
cd ..

# 复制示例配置文件
# Windows:
copy .env.example .env
# Mac/Linux:
# cp .env.example .env

# 编辑配置文件
# Windows:
notepad .env
# Mac/Linux:
# nano .env  或  vim .env
```

修改以下关键配置：

```env
LLM_API_KEY="sk-你的API密钥"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4o"
JWT_SECRET_KEY="aB3xK9mQ7wR2tY5nL8pV1cF4hJ6dS0gU"
```

> **获取 API Key：**
>
> - DeepSeek：去 [platform.deepseek.com](https://platform.deepseek.com) 注册并创建 API Key
> - OpenAI：去 [platform.openai.com](https://platform.openai.com) 获取
> - 其他兼容服务：修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可

#### 1.7 启动服务

**启动后端（终端 1）：**

```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端（终端 2）：**

```powershell
cd frontend
npm run dev
```

#### 1.8 访问系统

| 地址                           | 说明                |
| ---------------------------- | ----------------- |
| <http://localhost:5173>      | 🔥 **前端页面**（开发模式） |
| <http://localhost:8000/docs> | 后端 API 文档         |

***

### 二、再次启动项目的操作方法

当环境已配置好、依赖已安装后，再次启动项目只需以下步骤：

#### 2.1 进入项目目录

```powershell
cd EduAgent
```

#### 2.2 激活虚拟环境

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

#### 2.3 启动后端服务（终端 1）

```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2.4 启动前端服务（终端 2）

```powershell
cd frontend
npm run dev
```

#### 2.5 访问系统

打开浏览器访问 <http://localhost:5173> 即可。

> **注意事项：**
>
> - 如果修改了 `.env` 配置文件，需要重启后端服务才能生效
> - 如果更新了依赖（requirements.txt 或 package.json），需要重新执行安装命令

***

### 三、Docker 容器化启动指南

#### 3.1 环境准备

**安装 Docker Desktop（Windows/Mac）：**

1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. 双击安装，一路点"下一步"
3. 安装完成后启动 Docker Desktop，等待右下角图标变绿（蓝色鲸鱼图标）
4. 打开 PowerShell，输入以下命令验证安装：

```powershell
docker --version
docker compose version
```

**安装 Docker（Linux Ubuntu/Debian）：**

```bash
sudo apt update
sudo apt install docker.io docker-compose-v2 -y
sudo usermod -aG docker $USER
sudo service docker start
docker --version
```

#### 3.2 配置环境变量

```powershell
cd EduAgent

# 复制示例配置文件
# Windows:
copy .env.example .env
# Mac/Linux:
# cp .env.example .env

# 编辑配置文件
# Windows:
notepad .env
# Mac/Linux:
# nano .env  或  vim .env
```

修改配置（参考"一、初次启动项目"中的说明）。

#### 3.3 启动 Docker 容器

```powershell
# 进入 docker 目录
cd docker

# 启动服务（后台模式）
docker compose up -d
```

> **参数说明：**
>
> - `-d`：后台运行模式，容器在后台启动，不占用当前终端
> - `--build`：强制重新构建镜像（当修改了代码或配置后使用）
> - `--force-recreate`：强制重新创建容器

#### 3.4 查看容器状态

```powershell
# 查看所有容器状态
docker compose ps

# 查看后端服务日志
docker compose logs backend

# 实时查看日志（按 Ctrl+C 退出）
docker compose logs -f backend
```

#### 3.5 首次启动等待时间

首次启动会自动下载镜像、构建容器、安装依赖、创建数据库，大约需要 **2-5 分钟**。可以通过以下命令检查服务是否就绪：

```powershell
# 检查后端健康状态
docker compose exec backend curl http://localhost:8000/health
```

返回 `{"status": "healthy"}` 表示服务已就绪。

#### 3.6 访问系统

| 地址                           | 说明                |
| ---------------------------- | ----------------- |
| <http://localhost>           | 🔥 **前端页面**（主要使用） |
| <http://localhost:8000/docs> | 后端 API 文档         |

#### 3.7 停止和重启服务

```powershell
# 停止服务（数据保留）
docker compose down

# 重新启动服务
docker compose up -d

# 重新构建并启动（修改代码后）
docker compose up -d --build

# 完全重置（删除所有数据，慎用！）
docker compose down -v
```

#### 3.8 Docker Compose 配置说明

`docker/docker-compose.yml` 文件包含以下关键配置：

| 配置项                       | 说明                     | 默认值    |
| ------------------------- | ---------------------- | ------ |
| `BACKEND_PORT`            | 后端服务端口                 | 8000   |
| `FRONTEND_PORT`           | 前端服务端口                 | 80     |
| `DATABASE_URL`            | 数据库连接地址                | SQLite |
| `restart: unless-stopped` | 容器异常退出时自动重启            | -      |
| `healthcheck`             | 健康检查配置（每 30 秒检查一次）     | -      |
| `deploy.resources.limits` | 资源限制（内存 1536M，CPU 1.0） | -      |

> **注意事项：**
>
> - 如果端口被占用，修改 `.env` 文件中的 `BACKEND_PORT` 和 `FRONTEND_PORT`
> - 数据存储在 Docker Volume 中，执行 `docker compose down` 不会删除数据
> - 如需清理所有数据，执行 `docker compose down -v`

***

### 四、虚拟环境激活详细指南

本项目的虚拟环境激活脚本位于：`venv/Scripts/Activate.ps1`

#### 4.1 基础激活方法

**方法一：相对路径激活（推荐）**

```powershell
# 进入项目根目录
cd EduAgent

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

**方法二：绝对路径激活**

```powershell
# 使用完整绝对路径激活
& "e:\学校\大3\大三下\B-软件综合实践实验\Edu_Code\Agent_System\venv\Scripts\Activate.ps1"
```

#### 4.2 激活成功验证

激活成功后，终端提示符会显示：

```powershell
(venv) PS E:\学校\大3\大三下\B-软件综合实践实验\Edu_Code\Agent_System>
```

可以通过以下命令进一步验证：

```powershell
# 检查 Python 路径
where python
# 输出应指向 venv/Scripts/python.exe

# 检查虚拟环境变量
echo $env:VIRTUAL_ENV
# 输出应显示虚拟环境目录路径
```

#### 4.3 常见问题及解决方案

**问题 1：PowerShell 执行策略限制**

当执行 `.\venv\Scripts\Activate.ps1` 时报错：

```
无法加载文件 ...\Activate.ps1，因为在此系统上禁止运行脚本。
```

**解决方案：**

```powershell
# 以管理员身份打开 PowerShell，执行以下命令
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

按提示输入 `Y` 确认即可。

> **说明：**
>
> - `RemoteSigned` 策略允许本地脚本运行，但要求从互联网下载的脚本必须经过签名
> - `-Scope CurrentUser` 只对当前用户生效，无需管理员权限

**问题 2：激活脚本找不到**

确保当前工作目录是项目根目录：

```powershell
# 检查当前目录
pwd

# 确认 venv 目录存在
dir venv\Scripts
```

**问题 3：激活后不显示 (venv) 标识**

可以手动检查虚拟环境是否激活：

```powershell
# 检查 VIRTUAL_ENV 环境变量是否存在
if ($env:VIRTUAL_ENV) {
    Write-Host "虚拟环境已激活: $env:VIRTUAL_ENV"
} else {
    Write-Host "虚拟环境未激活"
}
```

#### 4.4 退出虚拟环境

```powershell
deactivate
```

执行后，终端提示符的 `(venv)` 标识会消失，系统恢复使用全局 Python 环境。

***

## 文档导航

| 文档                              | 说明              |
| ------------------------------- | --------------- |
| [后端文档](backend/docs/README.md)  | 后端技术栈、目录结构、核心逻辑 |
| [前端文档](frontend/docs/README.md) | 前端技术栈、目录结构、组件说明 |
| [API 文档](docs/API.md)           | 接口说明、使用示例       |
| [项目测试说明](测试文档/项目测试说明.md)        | 测试用例、测试报告、截图说明  |

***

## 常用命令

### Docker 部署

```powershell
# 启动服务
cd docker
docker compose up -d

# 查看后端日志
docker compose logs backend

# 实时查看日志
docker compose logs -f backend

# 查看所有容器状态
docker compose ps

# 停止服务（数据保留）
docker compose down

# 重新构建并启动
docker compose up -d --build

# 完全重置（删除所有数据，慎用！）
docker compose down -v

# 进入后端容器
docker compose exec backend bash
```

### 本地开发

```powershell
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

***

## 环境变量说明

| 变量               | 说明                              | 示例                          |
| ---------------- | ------------------------------- | --------------------------- |
| `LLM_API_KEY`    | API 密钥（**必填**）                  | sk-xxxx                     |
| `LLM_BASE_URL`   | API 接口地址                        | <https://api.openai.com/v1> |
| `LLM_MODEL`      | 模型名称                            | gpt-4o                      |
| `JWT_SECRET_KEY` | JWT 密钥（**必改**，不能以 `change-` 开头） | aB3xK9mQ...                 |
| `DATABASE_URL`   | 数据库连接地址（默认 SQLite）              | sqlite:///./edu\_agent.db   |
| `BACKEND_PORT`   | 后端端口（默认 8000）                   | 8000                        |
| `FRONTEND_PORT`  | 前端端口（默认 80）                     | 80                          |

***

## 常见问题

### Q：启动后页面打不开？

**A：** 首次启动需要 2-5 分钟初始化，等一会儿再刷新。如果还是不行：

```powershell
# Docker 方式
docker compose ps
docker compose logs backend

# 本地方式
# 检查后端是否启动成功，终端是否有报错信息
```

### Q：登录提示"账号密码错误"？

**A：** 确认使用的是正确的演示账号：

- 管理员：`admin` / `admin123`
- 学生：`student1` / `123456`

### Q：AI 聊天没有回复？

**A：** 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确填写：

```powershell
docker compose logs backend | Select-String ERROR
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

### Q：虚拟环境激活失败？

**A：** 参考"四、虚拟环境激活详细指南"中的常见问题及解决方案。

***

## 技术栈

| 分类    | 技术                      |
| ----- | ----------------------- |
| 后端框架  | Python 3.11 / FastAPI   |
| AI 框架 | LangGraph / LangChain   |
| 向量数据库 | FAISS                   |
| 数据库   | SQLite                  |
| 认证    | JWT / BCrypt            |
| 前端框架  | Vue 3 / Vite            |
| UI 组件 | Element Plus            |
| 状态管理  | Pinia                   |
| 容器化   | Docker / Docker Compose |
| 代理    | Nginx                   |

***

## License

MIT
