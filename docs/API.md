# EduAgent API 接口文档

> 后端 API 接口说明文档

---

## 目录

1. [基础信息](#1-基础信息)
2. [用户管理](#2-用户管理)
3. [用户画像](#3-用户画像)
4. [对话管理](#4-对话管理)
5. [AI 流式对话](#5-ai-流式对话)
6. [学习路径](#6-学习路径)
7. [学习资源](#7-学习资源)
8. [系统设置](#8-系统设置)
9. [管理后台](#9-管理后台)
10. [错误码](#10-错误码)

---

## 1. 基础信息

### 1.1 基础地址

| 环境 | 地址 |
|------|------|
| 本地开发 | http://localhost:8000 |
| Docker 部署 | http://localhost:8000 |

### 1.2 认证方式

使用 JWT Bearer Token 认证，在请求头中添加：

```
Authorization: Bearer <token>
```

### 1.3 响应格式

成功响应：
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

错误响应：
```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

---

## 2. 用户管理

### 2.1 用户登录

**POST** `/user/login`

请求体（form-urlencoded）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

示例：
```bash
curl -X POST http://localhost:8000/user/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "nickname": "管理员",
      "role": "admin"
    }
  }
}
```

### 2.2 用户注册

**POST** `/user/register`

请求体（JSON）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |
| nickname | string | 否 | 昵称 |

示例：
```bash
curl -X POST http://localhost:8000/user/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123","nickname":"测试用户"}'
```

响应：
```json
{
  "code": 200,
  "message": "注册成功",
  "data": null
}
```

### 2.3 获取当前用户信息

**GET** `/user/info`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/user/info \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "nickname": "管理员",
    "role": "admin",
    "major": "计算机科学"
  }
}
```

---

## 3. 用户画像

### 3.1 获取用户画像

**GET** `/portrait/me`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/portrait/me \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "portrait": {
      "id": 1,
      "name": "管理员",
      "major": "计算机科学",
      "course": "Python程序设计",
      "study_goal": "掌握Python编程",
      "knowledge_level": "65",
      "learning_preference": "visual",
      "learning_style": "视频学习",
      "weak_knowledge": "面向对象,异常处理",
      "raw_json": {
        "vark_scores": { "V": 70, "A": 60, "R": 55, "K": 75 }
      }
    }
  }
}
```

### 3.2 更新用户画像

**POST** `/portrait/update`

需要认证。

请求体（JSON）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| study_goal | string | 否 | 学习目标 |
| learning_preference | string | 否 | 认知风格 |
| learning_style | string | 否 | 学习方式 |
| weak_knowledge | string | 否 | 薄弱知识（逗号分隔） |

示例：
```bash
curl -X POST http://localhost:8000/portrait/update \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"study_goal":"精通深度学习","weak_knowledge":"卷积神经网络,Transformer"}'
```

响应：
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 3.3 分析学习风格

**POST** `/portrait/analyze-style`

需要认证。

示例：
```bash
curl -X POST http://localhost:8000/portrait/analyze-style \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "分析完成",
  "data": {
    "cognitive_style": "visual",
    "vark_scores": { "V": 70, "A": 60, "R": 55, "K": 75 },
    "recommendation": "建议使用视频教程和图表进行学习"
  }
}
```

---

## 4. 对话管理

### 4.1 获取会话列表

**GET** `/conversation/sessions`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/conversation/sessions \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "sessions": [
      {
        "session_id": "abc123",
        "preview": "如何学习Python?",
        "last_time": "2026-07-03 10:30:00"
      }
    ]
  }
}
```

### 4.2 获取会话内容

**GET** `/conversation/session/{session_id}`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/conversation/session/abc123 \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "role": "user",
      "content": "如何学习Python?",
      "create_time": "2026-07-03 10:30:00"
    },
    {
      "role": "assistant",
      "content": "学习Python可以从基础语法开始...",
      "create_time": "2026-07-03 10:30:15"
    }
  ]
}
```

### 4.3 删除会话

**DELETE** `/conversation/session/{session_id}`

需要认证。

示例：
```bash
curl -X DELETE http://localhost:8000/conversation/session/abc123 \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 5. AI 流式对话

### 5.1 SSE 流式对话

**POST** `/api/v1/chat/stream`

需要认证。使用 SSE（Server-Sent Events）协议返回流式响应。

请求体（JSON）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_content | string | 是 | 用户消息 |
| session_id | string | 否 | 会话ID，不传则新建 |

示例：
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_content":"解释什么是机器学习","session_id":"abc123"}'
```

响应（SSE 格式）：
```
data: {"content":"机器"}
data: {"content":"学习是"}
data: {"content":"一种"}
data: {"content":"人工智能"}
...
data: {"done": true}
```

### 5.2 多智能体流式对话

**POST** `/agent/chat/stream`

需要认证。使用 LangGraph 工作流进行多智能体对话。

请求体（JSON）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息 |

示例：
```bash
curl -X POST http://localhost:8000/agent/chat/stream \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我制定一个Python学习计划"}'
```

响应（SSE 格式）：
```
data: {"profile": {"knowledge_level": 65}}
data: {"rag": {"retrieved_docs": [...]}}
data: {"generator": {"generated_resource": {...}}}
data: {"guardrail": {"is_approved": true}}
data: {"planner": {"learning_path": [...]}}
```

---

## 6. 学习路径

### 6.1 获取学习路径列表

**GET** `/learning-path/list`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/learning-path/list \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "goal": "Python学习计划",
      "steps": [
        {"day": 1, "content": "学习Python基础语法"},
        {"day": 2, "content": "掌握数据类型和运算符"}
      ],
      "created_at": "2026-07-03 10:00:00"
    }
  ]
}
```

### 6.2 获取指定学习路径

**GET** `/learning-path/{goal}`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/learning-path/Python%E5%AD%A6%E4%B9%A0%E8%AE%A1%E5%88%92 \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "goal": "Python学习计划",
    "steps": [...],
    "created_at": "2026-07-03 10:00:00"
  }
}
```

### 6.3 保存学习路径

**POST** `/learning-path/save`

需要认证。

请求体（JSON）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goal | string | 是 | 学习目标 |
| steps | array | 是 | 步骤列表 |

示例：
```bash
curl -X POST http://localhost:8000/learning-path/save \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"goal":"深度学习入门","steps":[{"day":1,"content":"学习神经网络基础"}]}'
```

响应：
```json
{
  "code": 200,
  "message": "保存成功",
  "data": null
}
```

### 6.4 删除学习路径

**DELETE** `/learning-path/{goal}`

需要认证。

示例：
```bash
curl -X DELETE http://localhost:8000/learning-path/Python%E5%AD%A6%E4%B9%A0%E8%AE%A1%E5%88%92 \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 7. 学习资源

### 7.1 获取课程列表

**GET** `/resources/courses`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/resources/courses \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "name": "Python",
      "description": "Python程序设计课程",
      "files_count": 12
    },
    {
      "name": "Linux",
      "description": "Linux操作系统课程",
      "files_count": 8
    }
  ]
}
```

### 7.2 获取课程文件列表

**GET** `/resources/courses/{course_name}/files`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/resources/courses/Python/files \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {"name": "Python笔记.md", "size": "1024"},
    {"name": "Chapter1_Exercises.txt", "size": "512"}
  ]
}
```

### 7.3 下载文件

**GET** `/resources/download`

需要认证。

参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course | string | 是 | 课程名称 |
| path | string | 是 | 文件路径 |

示例：
```bash
curl -X GET "http://localhost:8000/resources/download?course=Python&path=Python%E7%AC%94%E8%AE%B0.md" \
  -H "Authorization: Bearer <token>" \
  -o Python笔记.md
```

### 7.4 预览文件

**GET** `/resources/preview`

需要认证。

参数：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course | string | 是 | 课程名称 |
| path | string | 是 | 文件路径 |

示例：
```bash
curl -X GET "http://localhost:8000/resources/preview?course=Python&path=Python%E7%AC%94%E8%AE%B0.md" \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": "# Python笔记\n\n## 第一章：基础语法",
    "file_type": "markdown"
  }
}
```

---

## 8. 系统设置

### 8.1 获取用户设置

**GET** `/user/settings`

需要认证。

示例：
```bash
curl -X GET http://localhost:8000/user/settings \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_key": "",
    "model": "gpt-4o",
    "temperature": 0.7
  }
}
```

### 8.2 保存用户设置

**PUT** `/user/settings`

需要认证。

请求体（JSON）：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| api_key | string | 否 | API密钥 |
| model | string | 否 | 模型名称 |
| temperature | float | 否 | 温度参数（0-1） |

示例：
```bash
curl -X PUT http://localhost:8000/user/settings \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","temperature":0.5}'
```

响应：
```json
{
  "code": 200,
  "message": "保存成功",
  "data": null
}
```

---

## 9. 管理后台

### 9.1 获取用户列表

**GET** `/admin/users`

需要认证且为管理员。

示例：
```bash
curl -X GET http://localhost:8000/admin/users \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "nickname": "管理员",
      "role": "admin",
      "create_time": "2026-01-01 00:00:00"
    }
  ]
}
```

### 9.2 获取资源统计

**GET** `/admin/stats/resources`

需要认证且为管理员。

示例：
```bash
curl -X GET http://localhost:8000/admin/stats/resources \
  -H "Authorization: Bearer <token>"
```

响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 10,
    "total_courses": 5,
    "total_files": 100,
    "total_conversations": 50
  }
}
```

---

## 10. 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效或过期） |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 1001 | 用户不存在 |
| 1002 | 密码错误 |
| 1003 | 用户已存在 |
| 1004 | JWT密钥未配置 |