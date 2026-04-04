# 快速启动指南

## 前置要求

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- FFmpeg

## 方式一：本地开发

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置以下项：
```
DATABASE_URL=postgresql+asyncpg://ainovel:ainovel@localhost:5432/ai_novel_media
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEEPSEEK_API_KEY=your-deepseek-key
```

### 3. 创建数据库

```bash
# 使用psql或其他工具创建数据库
createdb ai_novel_media
```

### 4. 初始化数据库表

```bash
# 方式1: 使用Alembic迁移
alembic upgrade head

# 方式2: 直接创建（开发环境）
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 5. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4
```

### 6. 启动Celery Worker（可选）

```bash
celery -A app.tasks worker --loglevel=info
```

## 方式二：Docker Compose

### 一键启动所有服务

```bash
cd backend
docker-compose up -d
```

这将启动：
- PostgreSQL数据库
- Redis缓存
- 后端API服务
- Celery Worker

### 查看日志

```bash
docker-compose logs -f backend
```

### 停止服务

```bash
docker-compose down
```

## 访问服务

- API文档: http://localhost:9000/docs
- ReDoc: http://localhost:9000/redoc
- 健康检查: http://localhost:9000/api/health

## 测试API

### 1. 注册用户

```bash
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

### 2. 登录获取令牌

```bash
curl -X POST http://localhost:9000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test1234"
  }'
```

### 3. 创建任务

```bash
curl -X POST http://localhost:9000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "task_type": "novel_only",
    "novel_config": {
      "length_type": "short",
      "genre": "male",
      "sub_genre": "xuanhuan"
    }
  }'
```

## 常见问题

### 数据库连接失败

检查PostgreSQL是否运行：
```bash
pg_isready
```

### Redis连接失败

检查Redis是否运行：
```bash
redis-cli ping
```

### 端口被占用

修改 `.env` 中的 `PORT` 配置或使用其他端口启动：
```bash
uvicorn app.main:app --port 9001
```

## 开发工具

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 代码格式化

```bash
pip install black isort
black app/
isort app/
```

### 类型检查

```bash
pip install mypy
mypy app/
```

## 下一步

1. 配置AI模型API密钥
2. 实现具体的Agent逻辑
3. 集成视频生成功能
4. 对接支付接口
5. 对接发布平台

## 获取帮助

- 查看 `README.md` 了解项目详情
- 查看 `PROJECT_SUMMARY.md` 了解项目结构
- 访问 API 文档查看接口详情
