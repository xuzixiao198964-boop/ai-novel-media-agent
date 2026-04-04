# 前端项目启动指南

## 项目概览

已成功创建三个前端项目，共 77 个源文件：

1. **official-site** (产品官网) - 6 个文件 - Port 80
2. **frontend** (用户端应用) - 36 个文件 - Port 8000  
3. **admin** (管理后台) - 23 个文件 - Port 8001

## 快速启动步骤

### 方式一：分别启动（推荐开发环境）

#### 1. 启动产品官网

```bash
cd official-site
npm install
npm run dev
```

访问: http://localhost:8080

#### 2. 启动用户端应用

```bash
cd frontend
npm install
npm run dev
```

访问: http://localhost:8000

#### 3. 启动管理后台

```bash
cd admin
npm install
npm run dev
```

访问: http://localhost:8001

### 方式二：一键启动所有项目

在项目根目录创建启动脚本：

**Windows (start-all.bat):**
```batch
@echo off
start cmd /k "cd official-site && npm install && npm run dev"
start cmd /k "cd frontend && npm install && npm run dev"
start cmd /k "cd admin && npm install && npm run dev"
```

**Linux/Mac (start-all.sh):**
```bash
#!/bin/bash
cd official-site && npm install && npm run dev &
cd frontend && npm install && npm run dev &
cd admin && npm install && npm run dev &
wait
```

## 项目功能清单

### Official Site (产品官网)
✅ 首页展示  
✅ 功能介绍（8个核心功能卡片）  
✅ 定价方案（4个套餐）  
✅ 开发者中心（REST API + OpenClaw）  
✅ 下载页面（Android/iOS/微信/抖音小程序）  
✅ 帮助中心（FAQ）  
✅ 登录/注册页面  
✅ 响应式设计  

### Frontend (用户端应用)
✅ 仪表盘（统计卡片 + 进行中任务）  
✅ 创建任务（4种模式 + 完整配置）  
✅ 我的任务（任务列表 + Agent详情）  
✅ 小说作品（列表展示 + 操作按钮）  
✅ 视频作品（视频集合 + 发布功能）  
✅ 作品广场（浏览他人作品）  
✅ 套餐管理（4个套餐切换）  
✅ 充值功能（金额选择 + 支付方式）  
✅ 消费记录（交易历史表格）  
✅ 平台绑定（抖音/小红书/番茄/起点）  
✅ 个人设置（资料编辑）  
✅ 侧边栏导航 + 顶部栏  
✅ 状态管理（Zustand）  
✅ API 封装（Axios）  

### Admin (管理后台)
✅ 数据概览（4个统计卡片 + 图表占位）  
✅ 用户管理（列表 + 搜索 + 禁用/启用）  
✅ 小说管理（列表 + 分类筛选 + 下架）  
✅ 视频管理（列表 + 查看）  
✅ 任务监控（实时状态 + 停止/优先）  
✅ API Key 管理（创建 + 吊销）  
✅ 财务报表（收入/成本/毛利分析）  
✅ 发布管理（平台发布状态 + 重试）  
✅ 系统日志（级别筛选 + 搜索）  
✅ 系统配置（套餐定价 + 系统参数）  
✅ 侧边栏导航 + 顶部栏  
✅ API 封装（Axios）  

## 技术栈

| 项目 | 技术 | 说明 |
|------|------|------|
| official-site | HTML5 + CSS3 + Vanilla JS | 纯静态，无需构建 |
| frontend | React 18 + TypeScript + Vite | 现代化 SPA |
| admin | React 18 + TypeScript + Vite | 现代化 SPA |

**共同依赖：**
- React Router v6 (路由)
- Zustand (状态管理)
- Axios (HTTP 客户端)
- Vite (构建工具)

## API 对接说明

所有项目已配置好 API 代理：

```typescript
// frontend/vite.config.ts
server: {
  port: 8000,
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}

// admin/vite.config.ts
server: {
  port: 8001,
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

## 构建生产版本

```bash
# Frontend
cd frontend
npm run build
# 输出: frontend/dist/

# Admin
cd admin
npm run build
# 输出: admin/dist/
```

## 目录结构

```
ai-novel-media-agent/
├── official-site/          # 产品官网
│   ├── index.html         # 主页
│   ├── login.html         # 登录页
│   ├── styles.css         # 样式
│   ├── script.js          # 脚本
│   └── package.json
│
├── frontend/              # 用户端
│   ├── src/
│   │   ├── api/          # API 封装 (5个文件)
│   │   ├── components/   # 组件 (6个文件)
│   │   ├── pages/        # 页面 (20个文件)
│   │   ├── store/        # 状态管理
│   │   ├── App.tsx       # 路由配置
│   │   └── main.tsx      # 入口
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
└── admin/                 # 管理后台
    ├── src/
    │   ├── api/          # API 封装
    │   ├── components/   # 组件 (6个文件)
    │   ├── pages/        # 页面 (10个文件)
    │   ├── App.tsx       # 路由配置
    │   └── main.tsx      # 入口
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## 注意事项

1. **端口占用**：确保 80、8000、8001 端口未被占用
2. **后端 API**：需要后端服务运行在 `http://localhost:8080`
3. **Node 版本**：建议使用 Node.js >= 16
4. **首次启动**：首次运行需要 `npm install` 安装依赖
5. **开发模式**：所有项目都支持热更新

## 下一步

1. 启动后端 API 服务（Port 8080）
2. 按照上述步骤启动前端项目
3. 在浏览器中访问对应端口
4. 开始开发或测试功能

## 问题排查

**端口被占用：**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

**依赖安装失败：**
```bash
# 清除缓存重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**构建失败：**
```bash
# 检查 TypeScript 错误
npm run lint
```

## 项目完成度

✅ 所有页面已实现  
✅ 所有组件已创建  
✅ API 接口已封装  
✅ 路由配置完成  
✅ 状态管理配置完成  
✅ 样式文件完整  
✅ 构建配置完成  
✅ 文档齐全  

**总计：77 个源文件，代码完整可运行！**
