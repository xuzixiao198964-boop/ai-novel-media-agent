#!/bin/bash

# 完整部署脚本：部署后端、前端、管理端到服务器
# 服务器: 104.244.90.202

set -e

SERVER_IP="104.244.90.202"
SERVER_USER="root"
SERVER_PASSWORD="vDyCuc83NxWw"

echo "========================================="
echo "AI智能内容创作平台 - 完整部署"
echo "========================================="

# 打包项目
echo "步骤 1: 打包项目文件"
cd /e/work/ai-novel-media-agent
tar --exclude='node_modules' --exclude='dist' --exclude='__pycache__' --exclude='.git' --exclude='*.pyc' -czf deploy-full.tar.gz backend/ admin/ official-site/

echo "步骤 2: 上传到服务器"
# 这里需要手动上传或使用其他工具
echo "请手动上传 deploy-full.tar.gz 到服务器 /tmp/ 目录"
echo "或使用: scp deploy-full.tar.gz root@104.244.90.202:/tmp/"
echo ""
echo "上传完成后，在服务器上执行以下命令："
echo ""
cat << 'SERVERSCRIPT'
#!/bin/bash
set -e

echo "步骤 3: 解压项目"
cd /opt
rm -rf ai-novel-media-agent
mkdir -p ai-novel-media-agent
cd ai-novel-media-agent
tar -xzf /tmp/deploy-full.tar.gz

echo "步骤 4: 安装后端依赖"
cd /opt/ai-novel-media-agent/backend
pip3 install -r requirements.txt

echo "步骤 5: 配置后端环境变量"
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

echo "步骤 6: 构建管理端"
cd /opt/ai-novel-media-agent/admin
npm install
npm run build

echo "步骤 7: 部署官网"
mkdir -p /var/www/html/ai-novel-media-agent
cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/ai-novel-media-agent/

echo "步骤 8: 配置Nginx"
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

echo "步骤 9: 配置后端服务"
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

echo "步骤 10: 验证部署"
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

SERVERSCRIPT
