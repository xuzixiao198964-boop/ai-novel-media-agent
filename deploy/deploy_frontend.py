#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署前端到服务器"""
import paramiko
import os
import sys
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

def deploy_frontend():
    print("[Deploy] Starting frontend deployment...")

    # 创建SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"[SSH] Connecting to {SERVER_IP}...")
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

        # 创建SFTP客户端
        sftp = ssh.open_sftp()

        # 1. 创建临时目录
        print("[Step 1] Creating temp directory...")
        ssh.exec_command("mkdir -p /tmp/frontend_deploy")

        # 2. 上传构建文件
        print("[Step 2] Uploading build files...")
        dist_path = Path("E:/work/ai-novel-media-agent/frontend/dist")

        def upload_dir(local_dir, remote_dir):
            for item in local_dir.iterdir():
                local_path = str(item)
                remote_path = f"{remote_dir}/{item.name}"

                if item.is_file():
                    print(f"  Uploading: {item.name}")
                    sftp.put(local_path, remote_path)
                elif item.is_dir():
                    ssh.exec_command(f"mkdir -p {remote_path}")
                    upload_dir(item, remote_path)

        upload_dir(dist_path, "/tmp/frontend_deploy")

        # 3. 备份旧文件
        print("[Step 3] Backing up old files...")
        stdin, stdout, stderr = ssh.exec_command("""
            if [ -d /var/www/app ]; then
                mv /var/www/app /var/www/app.backup.$(date +%Y%m%d_%H%M%S)
            fi
        """)
        stdout.channel.recv_exit_status()

        # 4. 部署新文件
        print("[Step 4] Deploying new files...")
        stdin, stdout, stderr = ssh.exec_command("""
            mkdir -p /var/www/app
            cp -r /tmp/frontend_deploy/* /var/www/app/
            chown -R www-data:www-data /var/www/app
            chmod -R 755 /var/www/app
            rm -rf /tmp/frontend_deploy
        """)
        stdout.channel.recv_exit_status()

        # 5. 更新Nginx配置
        print("[Step 5] Updating Nginx config...")
        nginx_config = """
server {
    listen 80;
    server_name _;

    # 产品官网
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 用户端应用
    location /app {
        alias /var/www/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    # API代理
    location /api {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:9000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:9000/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""

        # 写入Nginx配置
        with sftp.open('/etc/nginx/sites-available/default', 'w') as f:
            f.write(nginx_config)

        # 6. 重启Nginx
        print("[Step 6] Reloading Nginx...")
        stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("[OK] Nginx configured successfully")
        else:
            print("[ERROR] Nginx configuration failed")
            print(stderr.read().decode())
            return False

        # 7. 验证部署
        print("\n[Step 7] Verifying deployment...")
        import requests

        tests = [
            ("Official Site", "http://104.244.90.202/"),
            ("User App", "http://104.244.90.202/app/"),
            ("API Health", "http://104.244.90.202/api/health"),
        ]

        success_count = 0
        for name, url in tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"  [OK] {name}: {url}")
                    success_count += 1
                else:
                    print(f"  [WARN] {name}: {url} (status: {response.status_code})")
            except Exception as e:
                print(f"  [ERROR] {name}: {url} (error: {e})")

        print(f"\n[SUCCESS] Deployment completed! ({success_count}/{len(tests)} tests passed)")
        print("\n[URLs]")
        print("  - Official Site: http://104.244.90.202/")
        print("  - User App: http://104.244.90.202/app/")
        print("  - API Docs: http://104.244.90.202/docs")

        sftp.close()
        return True

    except Exception as e:
        print(f"[ERROR] Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_frontend()
