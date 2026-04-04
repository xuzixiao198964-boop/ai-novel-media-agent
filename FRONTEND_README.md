# AI Novel Media Agent - 前端项目

本目录包含三个前端项目，分别对应不同的用户界面和端口。

## 项目结构

```
ai-novel-media-agent/
├── official-site/          # 产品官网 (Port 80)
│   ├── index.html         # 主页
│   ├── login.html         # 登录页
│   ├── styles.css         # 样式文件
│   ├── script.js          # 交互脚本
│   ├── package.json
│   └── README.md
│
├── frontend/              # 用户端 Web 应用 (Port 8000)
│   ├── src/
│   │   ├── api/          # API 接口封装
│   │   ├── components/   # 公共组件
│   │   ├── pages/        # 页面组件
│   │   ├── store/        # 状态管理
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
│
└── admin/                 # 后台管理系统 (Port 8001)
    ├── src/
    │   ├── api/          # API 接口封装
    │   ├── components/   # 公共组件
    │   ├── pages/        # 页面组件
    │   ├── App.tsx
    │   └── main.tsx
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── README.md
```

## 快速启动

### 1. Official Site (产品官网)

```bash
cd official-site
npm install
npm run dev          # 开发环境 (Port 8080)
# 或
npm start            # 生产环境 (Port 80, 需要管理员权限)
```

访问: http://localhost:8080 (开发) 或 http://localhost (生产)

### 2. Frontend (用户端)

```bash
cd frontend
npm install
npm run dev          # 开发环境 (Port 8000)
```

访问: http://localhost:8000

### 3. Admin (管理后台)

```bash
cd admin
npm install
npm run dev          # 开发环境 (Port 8001)
```

访问: http://localhost:8001

## 技术栈对比

| 项目 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| official-site | HTML/CSS/JS | 80 | 纯静态网站，无需构建 |
| frontend | React + TypeScript + Vite | 8000 | 用户端应用，需要构建 |
| admin | React + TypeScript + Vite | 8001 | 管理后台，需要构建 |

## 功能特性

### Official Site (产品官网)
- 产品介绍和功能展示
- 定价方案
- API 文档和 OpenClaw 协议说明
- 下载页面（Android/iOS/小程序）
- 帮助中心
- 响应式设计

### Frontend (用户端)
- 仪表盘（任务概览、统计数据）
- 创建任务（小说/视频配置）
- 任务管理（进度追踪、Agent 详情）
- 作品管理（小说/视频列表、下载、发布）
- 作品广场（浏览分享）
- 套餐管理
- 充值功能
- 消费记录
- 平台绑定（抖音/小红书/番茄/起点）
- 个人设置

### Admin (管理后台)
- 数据概览（用户统计、收入趋势）
- 用户管理
- 小说/视频管理
- 任务监控
- API Key 管理
- 财务报表
- 发布管理
- 系统日志
- 系统配置

## API 对接

所有项目都通过代理方式对接后端 API：

- Frontend: `/api` → `http://localhost:8080`
- Admin: `/api/admin` → `http://localhost:8080`

## 构建生产版本

### Frontend

```bash
cd frontend
npm run build
# 构建产物在 dist/ 目录
```

### Admin

```bash
cd admin
npm run build
# 构建产物在 dist/ 目录
```

## 部署说明

### Official Site
直接部署 HTML/CSS/JS 文件到 Web 服务器即可。

### Frontend & Admin
1. 执行 `npm run build` 构建生产版本
2. 将 `dist/` 目录部署到 Web 服务器
3. 配置 Nginx 或其他服务器进行反向代理

示例 Nginx 配置：

```nginx
# Frontend
server {
    listen 8000;
    root /path/to/frontend/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8080;
    }
}

# Admin
server {
    listen 8001;
    root /path/to/admin/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8080;
    }
}
```

## 开发注意事项

1. 所有项目都已配置好与后端 API 的对接
2. Frontend 和 Admin 使用 Zustand 进行状态管理
3. 所有 API 调用都通过 Axios 封装
4. 使用 React Router v6 进行路由管理
5. 样式采用 CSS Modules 或独立 CSS 文件

## 环境要求

- Node.js >= 16
- npm >= 8

## 许可证

请参考项目根目录的 LICENSE 文件
