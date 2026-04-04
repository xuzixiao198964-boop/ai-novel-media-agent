# AI 智能内容创作平台 - 部署指南

## 快速部署

### 前置条件

1. 服务器信息：
   - IP: 104.244.90.202
   - 端口: 22
   - 用户: root
   - 密码: 8TbXfNYaywmW

2. 环境变量：
   ```bash
   export DEPLOY_SSH_PASSWORD='8TbXfNYaywmW'
   export LLM_API_KEY='your-deepseek-api-key'
   ```

### 一键部署

```bash
cd E:/work/ai-novel-media-agent/deploy
chmod +x deploy.sh
./deploy.sh
```

### 部署步骤说明

脚本会自动执行以下步骤：

1. **检查端口占用** - 停止占用 80, 8000, 8001, 9000 端口的进程
2. **清理旧数据** - 删除 /opt/ai-novel-media-agent 目录
3. **打包项目** - 创建 tar.gz 压缩包
4. **上传到服务器** - 通过 scp 上传
5. **安装依赖** - pip install 和 npm install
6. **配置环境** - 创建 .env 文件
7. **构建前端** - npm run build
8. **配置 Nginx** - 设置反向代理
9. **创建 systemd 服务** - 自动启动后端
10. **验证部署** - 测试所有端点

### 部署后验证

```bash
# 在服务器上运行
python3 /opt/ai-novel-media-agent/deploy/verify_deployment.py
```

或者本地运行：
```bash
cd E:/work/ai-novel-media-agent/deploy
python verify_deployment.py
```

### 访问地址

- 产品官网: http://104.244.90.202/
- 用户端: http://104.244.90.202:8000/
- 管理后台: http://104.244.90.202:8001/
- API 文档: http://104.244.90.202:9000/docs

### 查看日志

```bash
# 后端日志
sudo journalctl -u ai-novel-media-agent -f

# Nginx 日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart ai-novel-media-agent

# 重启 Nginx
sudo systemctl restart nginx
```

### 故障排查

#### 后端无法启动

```bash
# 检查服务状态
sudo systemctl status ai-novel-media-agent

# 查看详细日志
sudo journalctl -u ai-novel-media-agent -n 100 --no-pager

# 手动启动测试
cd /opt/ai-novel-media-agent/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
```

#### 端口被占用

```bash
# 查看端口占用
sudo lsof -i:9000
sudo lsof -i:80

# 停止占用进程
sudo kill -9 <PID>
```

#### 前端无法访问

```bash
# 检查 Nginx 配置
sudo nginx -t

# 重新加载配置
sudo nginx -s reload

# 检查文件权限
ls -la /opt/ai-novel-media-agent/frontend/dist/
```

## 手动部署

如果自动部署失败，可以手动执行：

### 1. 连接服务器

```bash
ssh root@104.244.90.202
```

### 2. 安装依赖

```bash
# Python 依赖
cd /opt/ai-novel-media-agent/backend
pip3 install -r requirements.txt

# Node.js 依赖
cd /opt/ai-novel-media-agent/frontend
npm install
npm run build

cd /opt/ai-novel-media-agent/admin
npm install
npm run build
```

### 3. 配置环境变量

```bash
cd /opt/ai-novel-media-agent/backend
cat > .env << EOF
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
HOST=0.0.0.0
PORT=9000
EOF
```

### 4. 启动服务

```bash
# 创建 systemd 服务
sudo cp /opt/ai-novel-media-agent/deploy/ai-novel-media-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-novel-media-agent
sudo systemctl start ai-novel-media-agent
```

### 5. 配置 Nginx

```bash
sudo cp /opt/ai-novel-media-agent/deploy/nginx.conf /etc/nginx/sites-available/ai-novel-media-agent
sudo ln -sf /etc/nginx/sites-available/ai-novel-media-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 更新部署

```bash
# 停止服务
sudo systemctl stop ai-novel-media-agent

# 更新代码
cd /opt/ai-novel-media-agent
# ... 上传新代码 ...

# 重新安装依赖（如果有变化）
cd backend && pip3 install -r requirements.txt
cd ../frontend && npm install && npm run build
cd ../admin && npm install && npm run build

# 重启服务
sudo systemctl start ai-novel-media-agent
sudo systemctl restart nginx
```

## 备份与恢复

### 备份

```bash
# 备份数据库
cp /opt/ai-novel-media-agent/backend/data/app.db /backup/app.db.$(date +%Y%m%d)

# 备份配置
tar -czf /backup/config.$(date +%Y%m%d).tar.gz /opt/ai-novel-media-agent/backend/.env
```

### 恢复

```bash
# 恢复数据库
cp /backup/app.db.20260404 /opt/ai-novel-media-agent/backend/data/app.db

# 重启服务
sudo systemctl restart ai-novel-media-agent
```
