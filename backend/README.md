# AI Novel Media Agent - Backend MVP

快速启动的最小可运行版本（MVP）

## 快速开始

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### 手动启动
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制环境变量文件
cp .env.example .env

# 5. 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能

### 1. 用户认证
- POST /auth/register - 注册
- POST /auth/login - 登录
- GET /auth/me - 获取当前用户信息

### 2. 任务管理
- POST /tasks/ - 创建任务
- GET /tasks/ - 获取任务列表
- GET /tasks/{task_id} - 获取任务详情

### 3. Agent功能（Mock版本）
- TrendAgent - 趋势分析（返回Mock数据）
- WriterAgent - 内容生成（返回Mock内容）

## 测试示例

### 注册用户
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 登录
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 创建趋势分析任务
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "trend_analysis",
    "input_data": {
      "keywords": ["玄幻", "修仙"],
      "platform": "douyin"
    }
  }'
```

### 创建写作任务
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "write_chapter",
    "input_data": {
      "title": "第一章 重生归来",
      "outline": "主角重生到十年前，获得系统",
      "style": "爽文",
      "length": 2000
    }
  }'
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── models.py         # 数据模型
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py       # 认证API
│   │   └── tasks.py      # 任务API
│   └── agents/
│       ├── __init__.py
│       ├── trend.py      # 趋势分析Agent
│       └── writer.py     # 写作Agent
├── data/                 # SQLite数据库目录（自动创建）
├── requirements.txt      # Python依赖
├── .env.example         # 环境变量模板
├── start.sh             # Linux/Mac启动脚本
└── start.bat            # Windows启动脚本
```

## 技术栈

- FastAPI - Web框架
- SQLAlchemy - ORM
- SQLite - 数据库（简化版）
- Pydantic - 数据验证
- JWT - 认证
- Bcrypt - 密码加密

## MVP特性

1. 使用SQLite而非PostgreSQL（无需额外安装）
2. Agent使用Mock数据（无需LLM API Key）
3. 同步数据库操作（简化代码）
4. 最小依赖集（快速安装）

## 下一步扩展

1. 集成真实的LLM API（DeepSeek/OpenAI）
2. 添加更多Agent（Planner, Reviser等）
3. 实现异步任务队列（Celery）
4. 切换到PostgreSQL
5. 添加视频生成功能
6. 实现多平台发布

## 注意事项

- 这是MVP版本，仅用于快速验证和开发
- 生产环境需要修改SECRET_KEY
- Mock数据仅供测试，实际使用需集成真实API
