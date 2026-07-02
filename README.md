# EduAgent

基于大模型的个性化学习多智能体系统 —— 一键 Docker 部署，无需配置环境。

---

## 快速开始（共 3 步，约 5 分钟）

### 准备工作：安装 Docker

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
# 重新登录终端使权限生效
sudo service docker start
docker --version   # 验证安装
```

---

### 第 1 步：配置 API Key（AI 聊天要用）

打开**终端**（Windows 用 PowerShell），进入项目文件夹：

```bash
# 先进入项目目录（根据实际位置调整）
cd EduAgent

# 复制环境变量模板
cp .env.example .env
```

然后用**记事本**（Windows）或任意文本编辑器打开 `.env` 文件：

```bash
# Windows PowerShell:
notepad .env

# Mac / Linux:
nano .env
```

找到这两行，修改成你自己的 API Key：

```env
LLM_API_KEY="sk-你的API密钥"
LLM_BASE_URL="https://api.openai.com/v1"
LLM_MODEL="gpt-4o"
```

② **JWT 密钥**（必改，**不能以 `change-` 开头**，否则后端会直接退出并触发 Docker 容器无限重启）：

```env
JWT_SECRET_KEY="aB3xK9mQ7wR2tY5nL8pV1cF4hJ6dS0gU"
```

> 建议改成至少 32 位的随机字符串（如 `openssl rand -base64 32` 的输出），不能留空，也不能保留 `.env.example` 里的 `change-me-...` 占位符。

> ❓ **没有 API Key？**
> - **DeepSeek**：去 [platform.deepseek.com](https://platform.deepseek.com) 注册 → 创建 API Key
> - **OpenAI**：去 [platform.openai.com](https://platform.openai.com) 获取
> - **其他兼容服务**：修改 `LLM_BASE_URL` 和 `LLM_MODEL` 即可

---

### 第 2 步：一键启动

打开**终端**，在项目目录下执行：

```bash
docker compose up -d
```

> 首次启动会自动下载镜像、安装依赖、创建数据库，**大约等 2-3 分钟**。之后启动只需几秒。

查看启动进度：

```bash
docker compose logs backend --tail=20
```

看到 `Uvicorn running on http://0.0.0.0:8000` 就说明启动完成。

---

### 第 3 步：打开浏览器

| 地址 | 说明 |
|------|------|
| http://localhost | 🔥 **前端页面**（主要使用） |
| http://localhost:8000/docs | 后端 API 文档 |

**演示账号（登录页面可看到）：**

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |
| `student1` | `123456` | 学生 |

---

## 常用命令

```bash
# 启动服务
docker compose up -d

# 查看后端日志（排查问题）
docker compose logs backend

# 停止服务（数据保留）
docker compose down

# 重新启动
docker compose up -d

# 完全重置（删除所有数据，慎用！）
docker compose down -v
```

---

## 环境变量说明

打开 `.env` 文件可以看到所有配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `LLM_API_KEY` | API 密钥（**必填**） | sk-xxxx |
| `LLM_BASE_URL` | API 接口地址 | https://api.openai.com/v1 |
| `LLM_MODEL` | 模型名称 | gpt-4o |
| `JWT_SECRET_KEY` | JWT 密钥（**必改**，不能以 `change-` 开头） | aB3xK9mQ... |
| `BACKEND_PORT` | 后端端口（默认 8000） | 8000 |
| `FRONTEND_PORT` | 前端端口（默认 80） | 80 |

> 如果 80 端口被占用（显示"无法连接"），修改 `.env` 中的 `FRONTEND_PORT=8080`，然后重新启动，访问 `http://localhost:8080`。

---

## 常见问题

### Q：启动后 http://localhost 打不开？

**A：** 首次启动需要 2-3 分钟初始化，等一会儿再刷新。如果还是不行：

```bash
# 查看后端是否正常运行
docker compose ps
# 查看日志找错误
docker compose logs backend
```

### Q：登录提示"账号密码错误"？

**A：** 确认使用的是正确的演示账号：
- 管理员：`admin` / `admin123`
- 学生：`student1` / `123456`

如果数据库被重置过，可能需要重新创建账号。

### Q：AI 聊天没有回复？

**A：** 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确填写：

```bash
docker compose logs backend | grep ERROR
```

### Q：Docker 提示"端口被占用"？

**A：** 修改 `.env` 中的端口号：

```env
BACKEND_PORT=8080
FRONT_PORT=8081
```

然后重新启动：`docker compose up -d`

### Q：Windows 提示"WSL integration not enabled"？

**A：**
1. 打开 Docker Desktop
2. 点击右上角 ⚙️ Settings
3. 选择 Resources → WSL Integration
4. 打开你的 WSL 发行版开关
5. 点击 Apply & Restart

### Q：`docker compose up -d` 后端容器不断重启，日志显示 "JWT_SECRET_KEY is not set or still uses default value"？

**A：** `.env` 中的 `JWT_SECRET_KEY` 不能以 `change-` 开头（系统会拒绝启动）。修改为随机字符串（至少 32 字符），然后重新启动：

```bash
notepad .env
# 修改 JWT_SECRET_KEY 为随机字符串
docker compose down
docker compose up -d
```

---

## 技术栈

Python 3.11 / FastAPI / LangGraph / FAISS / Vue 3 / Element Plus / SQLite / Docker / nginx

## License

MIT
