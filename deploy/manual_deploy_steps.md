# 手动部署步骤

## 服务器信息
- IP: 104.244.90.202
- 端口: 22
- 用户: root
- 密码: vDyCuc83NxWw

## 步骤 1: 上传项目文件

在本地已生成 `full-deploy.tar.gz`，请使用以下方式上传到服务器：

### 方式1: 使用WinSCP或其他SFTP工具
1. 连接到服务器 104.244.90.202:22
2. 上传 `E:\work\ai-novel-media-agent\full-deploy.tar.gz` 到 `/tmp/`

### 方式2: 使用scp命令（如果可用）
```bash
scp E:\work\ai-novel-media-agent\full-deploy.tar.gz root@104.244.90.202:/tmp/
```

## 步骤 2: SSH连接到服务器

```bash
ssh root@104.244.90.202
# 密码: vDyCuc83NxWw
```

## 步骤 3: 在服务器上执行部署

```bash
#!/bin/bash
set -e

echo "========================================="
echo "开始部署"
echo "========================================="

# 3.1 解压项目
echo "步骤 1: 解压项目"
cd /opt
rm -rf ai-novel-media-agent
mkdir -p ai-novel-media-agent
cd ai-novel-media-agent
tar -xzf /tmp/full-deploy.tar.gz

# 3.2 安装后端依赖
echo "步骤 2: 安装后端依赖"
cd /opt/ai-novel-media-agent/backend
pip3 install -r requirements.txt

# 3.3 配置后端环境变量
echo "步骤 3: 配置后端环境变量"
cat > .env << 'EOF'
LLM_API_KEY=sk-9fcc8f6d0ce94fdbbe66b152b7d3e485
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
HOST=0.0.0.0
PORT=9000
DATABASE_URL=sqlite:///./data/app.db
REDIS_URL=redis://localhost:6379/0
EOF

mkdir -p data/tasks data/uploads data/temp

# 3.4 构建管理端
echo "步骤 4: 构建管理端"
cd /opt/ai-novel-media-agent/admin
npm install
npm run build

# 3.5 部署官网
echo "步骤 5: 部署官网"
mkdir -p /var/www/html/ai-novel-media-agent
cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/ai-novel-media-agent/

# 3.6 配置Nginx
echo "步骤 6: 配置Nginx"
cat > /etc/nginx/sites-available/ai-novel-media-agent << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    # 产品官网
    location / {
        root /var/www/html/ai-novel-media-agent;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 管理后台
    location /admin {
        alias /opt/ai-novel-media-agent/admin/dist;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/ai-novel-media-agent /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 3.7 配置后端服务
echo "步骤 7: 配置后端服务"
cat > /etc/systemd/system/ai-novel-media-agent.service << 'SERVICEEOF'
[Unit]
Description=AI Novel Media Agent Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-novel-media-agent/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=3
Environment="PYTHONPATH=/opt/ai-novel-media-agent/backend"

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable ai-novel-media-agent
systemctl restart ai-novel-media-agent

# 3.8 验证部署
echo "步骤 8: 验证部署"
sleep 5
systemctl status ai-novel-media-agent --no-pager

echo "========================================="
echo "部署完成！"
echo "========================================="
echo "访问地址："
echo "  产品官网: http://104.244.90.202/"
echo "  管理后台: http://104.244.90.202/admin"
echo "  API文档: http://104.244.90.202:9000/docs"
echo ""
echo "查看日志："
echo "  journalctl -u ai-novel-media-agent -f"
```

## 步骤 4: 运行测试

### 4.1 单元测试
```bash
cd /opt/ai-novel-media-agent/backend
pytest tests/unit/ -v --tb=short
```

### 4.2 集成测试
```bash
cd /opt/ai-novel-media-agent/backend
pytest tests/integration/ -v --tb=short
```

### 4.3 查看测试覆盖率
```bash
cd /opt/ai-novel-media-agent/backend
pytest tests/ -v --cov=app --cov-report=html
```

## 步骤 5: 如果测试失败

1. 查看错误日志
2. 修复代码
3. 重新打包上传
4. 重新部署
5. 再次运行测试

## 常用命令

### 查看服务状态
```bash
systemctl status ai-novel-media-agent
```

### 查看日志
```bash
journalctl -u ai-novel-media-agent -f
```

### 重启服务
```bash
systemctl restart ai-novel-media-agent
```

### 测试API
```bash
curl http://localhost:9000/api/health
curl http://104.244.90.202/admin
```
