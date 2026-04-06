#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署用户端到服务器8000端口"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def execute_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("=" * 70)
    print("部署用户端到服务器8000端口")
    print("=" * 70)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 1. 检查frontend目录是否存在
        print("\n[1/8] 检查frontend目录...")
        check_cmd = """
if [ -d /opt/ai-novel-media-agent/frontend ]; then
    echo "frontend目录存在"
    ls -la /opt/ai-novel-media-agent/frontend/src/pages/*.tsx | wc -l | xargs echo "页面文件数:"
else
    echo "frontend目录不存在，需要上传"
fi
"""
        status, output, error = execute_ssh_command(ssh, check_cmd)
        print(output)

        # 2. 检查Node.js和npm
        print("\n[2/8] 检查Node.js环境...")
        check_node = """
node --version
npm --version
"""
        status, output, error = execute_ssh_command(ssh, check_node)
        print(output)

        # 3. 安装依赖
        print("\n[3/8] 安装前端依赖...")
        install_deps = """
cd /opt/ai-novel-media-agent/frontend
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
else
    echo "依赖已存在"
fi
"""
        status, output, error = execute_ssh_command(ssh, install_deps)
        print(output)
        if error:
            print(f"错误: {error}")

        # 4. 检查vite.config.ts配置
        print("\n[4/8] 检查Vite配置...")
        check_vite = """
cat /opt/ai-novel-media-agent/frontend/vite.config.ts
"""
        status, output, error = execute_ssh_command(ssh, check_vite)
        print(output)

        # 5. 构建前端
        print("\n[5/8] 构建前端...")
        build_cmd = """
cd /opt/ai-novel-media-agent/frontend
npm run build
"""
        status, output, error = execute_ssh_command(ssh, build_cmd)
        if status == 0:
            print("构建成功")
        else:
            print(f"构建输出: {output}")
            print(f"构建错误: {error}")

        # 6. 部署到Nginx目录
        print("\n[6/8] 部署到Nginx目录...")
        deploy_cmd = """
mkdir -p /var/www/ai-novel-media-agent/frontend
rm -rf /var/www/ai-novel-media-agent/frontend/*
cp -r /opt/ai-novel-media-agent/frontend/dist/* /var/www/ai-novel-media-agent/frontend/
ls -lh /var/www/ai-novel-media-agent/frontend/
"""
        status, output, error = execute_ssh_command(ssh, deploy_cmd)
        print(output)

        # 7. 配置Nginx
        print("\n[7/8] 配置Nginx...")
        nginx_config = """
cat > /etc/nginx/sites-available/ai-novel-media-agent-frontend << 'EOF'
server {
    listen 8000;
    server_name _;

    root /var/www/ai-novel-media-agent/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:9000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ai-novel-media-agent-frontend /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
"""
        status, output, error = execute_ssh_command(ssh, nginx_config)
        print(output)
        if error:
            print(f"错误: {error}")

        # 8. 验证部署
        print("\n[8/8] 验证部署...")
        verify_cmd = """
echo "检查Nginx配置:"
nginx -t

echo ""
echo "检查8000端口:"
netstat -tlnp | grep 8000

echo ""
echo "检查前端文件:"
ls -lh /var/www/ai-novel-media-agent/frontend/index.html

echo ""
echo "测试HTTP访问:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/

echo ""
echo "测试API代理:"
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8000/api/health
"""
        status, output, error = execute_ssh_command(ssh, verify_cmd)
        print(output)

        ssh.close()

        print("\n" + "=" * 70)
        print("部署完成")
        print("=" * 70)
        print("\n访问地址: http://104.244.90.202:8000")
        print("\n说明:")
        print("- 用户端已部署到8000端口")
        print("- API请求会代理到后端9000端口")
        print("- 需要注册/登录后才能使用")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
