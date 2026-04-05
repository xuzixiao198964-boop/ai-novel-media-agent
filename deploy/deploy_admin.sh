#!/bin/bash

# 部署管理端到服务器80端口/admin路径
# 服务器: 104.244.90.202

set -e

SERVER_IP="104.244.90.202"
SERVER_USER="root"
SERVER_PASSWORD="vDyCuc83NxWw"

echo "========================================="
echo "部署管理端到服务器"
echo "========================================="

# 使用SSH执行远程命令
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

echo "步骤 1: 创建部署目录"
mkdir -p /opt/ai-novel-media-agent/admin
cd /opt/ai-novel-media-agent

echo "步骤 2: 检查是否已有admin代码"
if [ ! -d "admin/src" ]; then
    echo "错误: admin源码不存在，需要先上传代码"
    exit 1
fi

echo "步骤 3: 安装依赖"
cd /opt/ai-novel-media-agent/admin
npm install

echo "步骤 4: 构建admin项目"
npm run build

echo "步骤 5: 配置Nginx"
# 更新Nginx配置，添加/admin路径
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

echo "步骤 6: 重启Nginx"
ln -sf /etc/nginx/sites-available/ai-novel-media-agent /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

echo "========================================="
echo "部署完成！"
echo "========================================="
echo "访问地址: http://104.244.90.202/admin"

ENDSSH

echo ""
echo "验证部署..."
sleep 3
curl -I http://${SERVER_IP}/admin || echo "警告: 无法访问管理后台"
