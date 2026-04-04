# 管理后台系统部署指南

## 系统概述

完整的管理后台系统，包含前后端所有功能，严格按照原型设计实现。

## 功能模块（10个）

### 1. 数据概览 (Dashboard)
- 用户总数、今日新增
- 活跃任务、排队任务
- 今日收入、增长率
- 作品总数统计
- 收入趋势图表（30天）
- 最近注册用户列表

### 2. 用户管理 (Users)
- 用户列表（分页、搜索）
- 用户详情查看
- 启用/禁用用户
- 套餐管理
- 余额管理
- 按套餐、状态筛选

### 3. 小说管理 (Novels)
- 小说列表（分页、搜索）
- 按分类筛选
- 上架/下架管理
- 删除小说
- 字数、评分、浏览量统计

### 4. 视频管理 (Videos)
- 视频列表（分页）
- 视频类型筛选
- 时长、集数显示
- 状态管理

### 5. 任务监控 (Tasks)
- 实时任务统计（运行中、排队、完成、失败）
- 任务列表（自动刷新）
- 任务进度显示
- 当前Agent显示
- 停止任务功能

### 6. API Key管理 (ApiKeys)
- API Key列表
- 创建新Key
- 吊销Key
- 使用次数统计
- 限流配置

### 7. 财务报表 (Finance)
- 本月收入、成本、毛利
- 毛利率计算
- 收入vs成本趋势图（30天）
- 收入来源分析

### 8. 发布管理 (Publish)
- 发布记录列表
- 发布状态（成功、审核中、失败）
- 重试失败的发布
- 平台信息显示

### 9. 系统日志 (Logs)
- 日志列表（分页）
- 按级别筛选（ERROR、WARN、INFO）
- 关键词搜索
- 时间、模块、消息显示

### 10. 系统配置 (Config)
- 套餐定价配置
  - 基础版、进阶版、专业版、企业版
  - 小说单价、视频单价
- 系统参数配置
  - 计费倍率范围
  - 最大并发任务数
  - 发布模式（mock/production）

## 技术栈

### 前端
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS (样式)
- Zustand (状态管理)
- React Router (路由)
- Recharts (图表)
- Axios (HTTP客户端)

### 后端
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL (数据库)
- Pydantic (数据验证)

## 数据库模型

已完善的模型：
- User (用户) - 增加了role, subscription_tier, balance, is_active等字段
- Task (任务) - 增加了progress, current_agent, error_message等字段
- Novel (小说) - 增加了category, word_count等字段
- Video (视频) - 增加了video_type, episode_count等字段
- Payment (支付) - 新增模型
- APIKey (API密钥) - 新增模型
- PublishRecord (发布记录) - 新增模型
- SystemLog (系统日志) - 新增模型
- SystemConfig (系统配置) - 新增模型

## 后端API接口

所有接口位于 `backend/app/api/admin.py`：

### 数据概览
- GET /api/admin/dashboard - 获取仪表盘统计
- GET /api/admin/dashboard/income-trend - 收入趋势
- GET /api/admin/dashboard/recent-users - 最近用户

### 用户管理
- GET /api/admin/users - 用户列表
- GET /api/admin/users/{id} - 用户详情
- PATCH /api/admin/users/{id} - 更新用户

### 小说管理
- GET /api/admin/novels - 小说列表
- PATCH /api/admin/novels/{id}/status - 更新状态
- DELETE /api/admin/novels/{id} - 删除小说

### 视频管理
- GET /api/admin/videos - 视频列表

### 任务监控
- GET /api/admin/tasks/stats - 任务统计
- GET /api/admin/tasks - 任务列表
- POST /api/admin/tasks/{id}/stop - 停止任务

### API Key管理
- GET /api/admin/api-keys - Key列表
- POST /api/admin/api-keys - 创建Key
- DELETE /api/admin/api-keys/{id} - 吊销Key

### 财务报表
- GET /api/admin/finance/summary - 财务汇总
- GET /api/admin/finance/trend - 财务趋势

### 发布管理
- GET /api/admin/publish - 发布记录
- POST /api/admin/publish/{id}/retry - 重试发布

### 系统日志
- GET /api/admin/logs - 日志列表

### 系统配置
- GET /api/admin/config - 所有配置
- GET /api/admin/config/{key} - 单个配置
- PUT /api/admin/config - 更新配置

## 部署步骤

### 1. 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 创建管理员账号（需要在数据库中手动设置role='admin'）
# 或通过脚本创建

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端部署

```bash
cd admin

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 构建产物在 dist/ 目录
```

### 3. 配置

#### 前端配置 (vite.config.ts)
```typescript
server: {
  port: 3001,
  proxy: {
    '/api': {
      target: 'http://your-backend-url:8000',
      changeOrigin: true
    }
  }
}
```

#### 后端配置
确保在 `backend/app/core/deps.py` 中实现了 `get_current_admin` 依赖：

```python
async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="需要管理员权限"
        )
    return current_user
```

### 4. Nginx配置（生产环境）

```nginx
server {
    listen 80;
    server_name admin.yourdomain.com;

    # 前端静态文件
    location / {
        root /path/to/admin/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 样式说明

严格按照原型设计实现：
- 侧边栏：220px宽，深色背景 (#111827)
- 激活菜单项：红色高亮 (#f87171)，左侧3px边框
- 卡片：白色背景，圆角12px，边框 #e5e7eb
- 徽章：圆角20px，不同状态不同颜色
- 表格：斑马纹，悬停高亮
- 按钮：圆角6px，indigo主色调

## 默认登录

需要在数据库中创建管理员账号：

```sql
-- 创建管理员用户
INSERT INTO users (username, email, hashed_password, role, subscription_tier, is_active)
VALUES ('admin', 'admin@example.com', '$hashed_password', 'admin', 'enterprise', true);
```

## 测试数据

可以使用以下脚本生成测试数据：

```python
# backend/scripts/seed_admin_data.py
# 生成用户、任务、小说、视频等测试数据
```

## 注意事项

1. **权限控制**：所有管理接口都需要管理员权限
2. **数据库迁移**：部署前确保运行所有迁移
3. **环境变量**：配置数据库连接、JWT密钥等
4. **CORS配置**：确保后端允许前端域名访问
5. **日志记录**：建议配置日志自动写入SystemLog表

## 目录结构

```
admin/
├── src/
│   ├── api/           # API客户端
│   │   ├── client.ts  # Axios配置
│   │   └── index.ts   # 所有API接口
│   ├── components/    # 组件
│   │   ├── Layout.tsx
│   │   ├── Sidebar.tsx
│   │   └── Topbar.tsx
│   ├── pages/         # 页面（10个）
│   │   ├── Dashboard.tsx
│   │   ├── Users.tsx
│   │   ├── Novels.tsx
│   │   ├── Videos.tsx
│   │   ├── Tasks.tsx
│   │   ├── ApiKeys.tsx
│   │   ├── Finance.tsx
│   │   ├── Publish.tsx
│   │   ├── Logs.tsx
│   │   ├── Config.tsx
│   │   └── Login.tsx
│   ├── store/         # 状态管理
│   │   └── auth.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json

backend/app/api/
└── admin.py          # 完整的管理API（600+行）
```

## 功能特性

- ✅ 完全按照原型设计实现UI
- ✅ 所有10个功能模块完整实现
- ✅ 前后端完全打通
- ✅ 实时数据刷新（任务监控）
- ✅ 图表可视化（Recharts）
- ✅ 分页、搜索、筛选
- ✅ 响应式设计
- ✅ 错误处理
- ✅ 权限控制
- ✅ TypeScript类型安全

## 下一步

1. 运行数据库迁移创建新表
2. 创建管理员账号
3. 启动后端服务
4. 启动前端开发服务器
5. 访问 http://localhost:3001 登录测试

## 支持

如有问题，请检查：
1. 后端服务是否正常运行
2. 数据库连接是否正常
3. 管理员账号是否创建
4. API代理配置是否正确
