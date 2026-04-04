# AI 智能内容创作平台

> **版本**: 2.0 | **日期**: 2026-04-04  
> **整合项目**: ai-novel-agent + media-agent

---

## 项目概述

本平台整合 **AI 小说自动生成**（ai-novel-agent）与 **资讯/视频自动制作**（media-agent）两大核心能力，面向 C 端用户提供一站式"AI 内容创作 → 视频制作 → 多平台分发"的完整解决方案。

### 核心功能

- 📖 **AI 小说生成**：微小说到超长篇，儿童/男频/女频全题材覆盖
- 🎬 **智能视频制作**：小说/资讯自动转视频，AI 画面生成
- 📰 **资讯视频化**：RSS 抓取，大模型归纳，口语化述说
- 🚀 **多平台发布**：自动发布到抖音、小红书、番茄小说、起点等
- 💰 **灵活计费**：按需付费，小说按千字、视频按秒计费
- 🔌 **开放 API**：RESTful API + OpenClaw 协议

---

## 项目结构

```
ai-novel-media-agent/
├── backend/                    # 后端服务 (Port 9000)
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── agents/            # 7 个 Agent
│   │   ├── api/               # API 路由
│   │   ├── services/          # 业务服务
│   │   ├── models.py          # 数据库模型
│   │   └── ...
│   ├── tests/                 # 测试
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # 用户端 Web (Port 8000)
│   ├── src/
│   │   ├── pages/             # 页面组件
│   │   ├── components/        # 公共组件
│   │   ├── api.ts             # API 封装
│   │   └── ...
│   └── package.json
│
├── admin/                      # 后台管理 (Port 8001)
│   ├── src/
│   │   ├── pages/
│   │   └── ...
│   └── package.json
│
├── official-site/              # 产品官网 (Port 80)
│   ├── index.html
│   ├── pricing.html
│   └── ...
│
├── deploy/                     # 部署脚本
│   ├── deploy.sh
│   ├── docker-compose.yml
│   └── nginx.conf
│
└── docs/                       # 文档
    ├── 需求规格说明书.md
    ├── 架构设计.md
    ├── 详细设计.md
    ├── 单元测试设计.md
    ├── 集成测试设计.md
    └── 部署架构说明.md
```

---

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ (可选)
- Redis 6+ (可选)
- FFmpeg 4.4+

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置 LLM API Key 等
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### 前端启动

```bash
# 用户端
cd frontend
npm install
npm run dev

# 管理后台
cd admin
npm install
npm run dev

# 官网（使用任意静态服务器）
cd official-site
python -m http.server 80
```

---

## 部署到服务器

### 服务器信息

- **IP**: 104.244.90.202
- **端口**: 22
- **用户**: root
- **密码**: 8TbXfNYaywmW

### 自动部署

```bash
# 设置环境变量
export DEPLOY_SSH_PASSWORD='8TbXfNYaywmW'
export LLM_API_KEY='your-deepseek-key'

# 执行部署
cd deploy
./deploy.sh
```

### 手动部署

详见 [部署架构说明.md](docs/部署架构说明.md)

---

## 测试

### 单元测试

```bash
cd backend
pytest tests/unit/ -v --cov=app
```

### 集成测试

```bash
cd backend
pytest tests/integration/ -v
```

### E2E 测试

```bash
cd frontend
npx playwright test
```

---

## API 文档

启动后端服务后访问：

- Swagger UI: http://localhost:9000/docs
- ReDoc: http://localhost:9000/redoc

---

## 技术栈

### 后端

- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **任务队列**: Celery
- **AI 模型**: DeepSeek / Gemini / OpenAI
- **视频处理**: FFmpeg

### 前端

- **框架**: React 18 + TypeScript
- **状态管理**: Zustand
- **路由**: React Router
- **UI**: Tailwind CSS
- **构建**: Vite

### 部署

- **容器化**: Docker + docker-compose
- **反向代理**: Nginx
- **进程管理**: systemd

---

## 开发团队

- **项目负责人**: AI Assistant
- **开发时间**: 2026-04-04
- **版本**: 2.0

---

## 许可证

MIT License

---

## 相关链接

- [需求规格说明书](docs/需求规格说明书.md)
- [架构设计](docs/架构设计.md)
- [详细设计](docs/详细设计.md)
- [测试设计](docs/单元测试设计.md)
- [部署说明](docs/部署架构说明.md)
