# Official Site - 产品官网

纯 HTML/CSS/JS 实现的产品官网，Port 80

## 功能特性

- 首页展示
- 功能介绍
- 定价方案
- 开发者中心（API 文档、OpenClaw 协议）
- 下载页面（Android/iOS/小程序）
- 帮助中心
- 响应式设计

## 启动方式

```bash
# 安装依赖
npm install

# 开发环境（Port 8080）
npm run dev

# 生产环境（Port 80，需要管理员权限）
npm start
```

## 文件结构

```
official-site/
├── index.html          # 主页
├── login.html          # 登录页
├── styles.css          # 样式文件
├── script.js           # 交互脚本
├── package.json        # 项目配置
└── README.md          # 说明文档
```

## 技术栈

- HTML5
- CSS3
- Vanilla JavaScript
- http-server（开发服务器）
