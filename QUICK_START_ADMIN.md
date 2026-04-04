# 管理后台系统 - 快速启动指南

## 系统概述

完整的管理后台系统，包含10个功能模块，前后端完全打通。

## 一键启动

### 1. 后端启动

```bash
# 进入后端目录
cd E:/work/ai-novel-media-agent/backend

# 安装依赖（首次）
pip install -r requirements.txt

# 创建管理员账号（首次）
python scripts/create_admin.py

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将运行在: http://localhost:8000

### 2. 前端启动

```bash
# 进入前端目录
cd E:/work/ai-novel-media-agent/admin

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端服务将运行在: http://localhost:3001

### 3. 访问系统

打开浏览器访问: http://localhost:3001

**默认登录信息:**
- 用户名: `admin`
- 密码: `admin123`

⚠️ 首次登录后请立即修改密码！

## 功能模块

系统包含10个完整的功能模块：

1. **📊 数据概览** - 实时统计和趋势图表
2. **👥 用户管理** - 用户列表、启用/禁用、套餐管理
3. **📖 小说管理** - 小说审核、上下架管理
4. **🎬 视频管理** - 视频作品查看和管理
5. **📋 任务监控** - 实时任务状态监控（自动刷新）
6. **🔑 API Key管理** - API密钥创建和管理
7. **💰 财务报表** - 收入成本分析和趋势
8. **📤 发布管理** - 内容发布记录和重试
9. **📝 系统日志** - 系统运行日志查询
10. **⚙️ 系统配置** - 套餐定价和系统参数

## 目录结构

```
E:/work/ai-novel-media-agent/
├── admin/                          # 前端代码
│   ├── src/
│   │   ├── api/                   # API客户端
│   │   ├── components/            # 公共组件
│   │   ├── pages/                 # 11个页面组件
│   │   ├── store/                 # 状态管理
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
├── backend/                        # 后端代码
│   ├── app/
│   │   ├── api/
│   │   │   └── admin.py          # 管理API（839行）
│   │   └── models.py             # 数据模型（9个）
│   └── scripts/
│       └── create_admin.py       # 创建管理员
└── docs/
    └── prototype/
        └── admin.html            # 原型设计
```

## 技术栈

### 前端
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS (样式)
- Zustand (状态管理)
- React Router (路由)
- Recharts (图表)

### 后端
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

## 常见问题

### Q1: 后端启动失败？
**A:** 检查以下几点：
1. 数据库是否正常运行
2. 环境变量是否配置正确
3. 依赖是否完整安装

### Q2: 前端无法连接后端？
**A:** 检查：
1. 后端服务是否启动（http://localhost:8000）
2. vite.config.ts 中的代理配置是否正确
3. 浏览器控制台是否有CORS错误

### Q3: 登录失败？
**A:** 确认：
1. 管理员账号是否创建（运行 create_admin.py）
2. 用户名密码是否正确
3. 后端日志是否有错误信息

### Q4: 数据不显示？
**A:** 检查：
1. 数据库中是否有数据
2. API接口是否正常返回
3. 浏览器Network标签查看请求状态

## 生产部署

### 前端构建
```bash
cd admin
npm run build
# 产物在 dist/ 目录
```

### 部署到Nginx
```nginx
server {
    listen 80;
    server_name admin.yourdomain.com;
    
    # 前端静态文件
    location / {
        root /path/to/admin/dist;
        try_files $uri /index.html;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 开发建议

### 前端开发
```bash
cd admin
npm run dev  # 启动开发服务器（热重载）
```

### 后端开发
```bash
cd backend
uvicorn app.main:app --reload  # 启动开发服务器（自动重载）
```

### 代码格式化
```bash
# 前端
cd admin
npm run lint

# 后端
cd backend
black app/
flake8 app/
```

## 文档链接

- **完整部署指南**: ADMIN_DEPLOYMENT.md
- **功能总结**: ADMIN_SUMMARY.md
- **交付报告**: DELIVERY_REPORT.md
- **前端说明**: admin/README.md

## 支持

如遇问题，请检查：
1. 后端日志: 查看控制台输出
2. 前端日志: 浏览器开发者工具 Console
3. 网络请求: 浏览器开发者工具 Network
4. 数据库状态: 检查数据库连接和数据

## 下一步

1. ✅ 启动后端服务
2. ✅ 启动前端服务
3. ✅ 登录系统
4. ✅ 浏览各个功能模块
5. ✅ 修改默认密码
6. ✅ 配置系统参数
7. ✅ 开始使用

---

**快速启动完成！** 🎉

现在你可以访问 http://localhost:3001 开始使用管理后台系统。
