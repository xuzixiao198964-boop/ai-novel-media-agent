#!/bin/bash

# AI 智能内容创作平台 - 自动部署脚本
# 服务器: 104.244.90.202

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI 智能内容创作平台 - 自动部署${NC}"
echo -e "${GREEN}========================================${NC}"

# 配置
SERVER_IP="104.244.90.202"
SERVER_USER="root"
SERVER_PASSWORD="${DEPLOY_SSH_PASSWORD}"
LLM_API_KEY="${LLM_API_KEY}"

if [ -z "$SERVER_PASSWORD" ]; then
    echo -e "${RED}错误: 请设置 DEPLOY_SSH_PASSWORD 环境变量${NC}"
    exit 1
fi

if [ -z "$LLM_API_KEY" ]; then
    echo -e "${RED}错误: 请设置 LLM_API_KEY 环境变量${NC}"
    exit 1
fi

# 检查 sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}安装 sshpass...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install hudochenkov/sshpass/sshpass
    else
        sudo apt-get install -y sshpass
    fi
fi

echo -e "${GREEN}步骤 1: 检查服务器端口占用${NC}"
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    echo "检查端口占用情况..."

    # 检查并停止占用端口的进程
    for port in 80 8000 8001 9000; do
        pid=$(lsof -ti:$port || true)
        if [ ! -z "$pid" ]; then
            echo "端口 $port 被进程 $pid 占用，正在停止..."
            kill -9 $pid || true
            sleep 1
        fi
    done

    # 停止相关的 systemd 服务
    systemctl stop media-agent 2>/dev/null || true
    systemctl stop ai-novel-agent 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true

    echo "端口清理完成"
EOF

echo -e "${GREEN}步骤 2: 清理服务器旧数据${NC}"
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << 'EOF'
    echo "清理旧数据..."
    rm -rf /opt/ai-novel-media-agent
    rm -rf /var/www/html/ai-novel-media-agent
    echo "旧数据清理完成"
EOF

echo -e "${GREEN}步骤 3: 打包项目文件${NC}"
cd ..
tar -czf deploy/ai-novel-media-agent.tar.gz \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='dist' \
    --exclude='build' \
    backend/ frontend/ admin/ official-site/ deploy/

echo -e "${GREEN}步骤 4: 上传到服务器${NC}"
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no \
    deploy/ai-novel-media-agent.tar.gz \
    $SERVER_USER@$SERVER_IP:/tmp/

echo -e "${GREEN}步骤 5: 在服务器上部署${NC}"
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP << EOF
    set -e

    echo "解压项目文件..."
    mkdir -p /opt/ai-novel-media-agent
    cd /opt/ai-novel-media-agent
    tar -xzf /tmp/ai-novel-media-agent.tar.gz
    rm /tmp/ai-novel-media-agent.tar.gz

    echo "安装后端依赖..."
    cd /opt/ai-novel-media-agent/backend
    pip3 install -r requirements.txt

    echo "配置环境变量..."
    cat > .env << 'ENVEOF'
LLM_API_KEY=$LLM_API_KEY
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
HOST=0.0.0.0
PORT=9000
DATABASE_URL=sqlite:///./data/app.db
REDIS_URL=redis://localhost:6379/0
ENVEOF

    echo "创建数据目录..."
    mkdir -p data/tasks data/uploads data/temp

    echo "安装前端依赖并构建..."
    cd /opt/ai-novel-media-agent/frontend
    npm install
    npm run build

    cd /opt/ai-novel-media-agent/admin
    npm install
    npm run build

    echo "配置 Nginx..."
    mkdir -p /var/www/html/ai-novel-media-agent
    cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/ai-novel-media-agent/

    cat > /etc/nginx/sites-available/ai-novel-media-agent << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    # 产品官网
    location / {
        root /var/www/html/ai-novel-media-agent;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 用户端 Web
    location /app {
        alias /opt/ai-novel-media-agent/frontend/dist;
        try_files \$uri \$uri/ /app/index.html;
    }

    # 管理后台
    location /admin {
        alias /opt/ai-novel-media-agent/admin/dist;
        try_files \$uri \$uri/ /admin/index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
NGINXEOF

    ln -sf /etc/nginx/sites-available/ai-novel-media-agent /etc/nginx/sites-enabled/
    nginx -t && systemctl restart nginx

    echo "创建 systemd 服务..."
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
    systemctl start ai-novel-media-agent

    echo "等待服务启动..."
    sleep 5

    echo "检查服务状态..."
    systemctl status ai-novel-media-agent --no-pager || true
EOF

echo -e "${GREEN}步骤 6: 验证部署${NC}"
echo "等待服务完全启动..."
sleep 10

echo "测试后端 API..."
curl -f http://$SERVER_IP:9000/api/health || echo -e "${YELLOW}警告: 后端 API 未响应${NC}"

echo "测试产品官网..."
curl -f http://$SERVER_IP/ || echo -e "${YELLOW}警告: 产品官网未响应${NC}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "访问地址："
echo "  产品官网: http://$SERVER_IP/"
echo "  用户端: http://$SERVER_IP/app"
echo "  管理后台: http://$SERVER_IP/admin"
echo "  API 文档: http://$SERVER_IP:9000/docs"
echo ""
echo "查看日志："
echo "  sudo journalctl -u ai-novel-media-agent -f"
echo ""
