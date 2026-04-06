#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署用户端前端"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        
        print("检查用户端源码...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-novel-media-agent/frontend/src/pages/Login.tsx")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        if 'No such file' in output:
            print("✗ 源码不存在，需要先上传")
            return 1
        print("✓ 源码存在")
        
        print("\n检查Login.tsx中的登录方式...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 5 'type=' /opt/ai-novel-media-agent/frontend/src/pages/Login.tsx | head -10")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n构建用户端前端...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/frontend && npm run build 2>&1")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if 'built in' in output or 'Build completed' in output:
            print("✓ 构建成功")
        else:
            print("构建输出:")
            print(output[-500:] if len(output) > 500 else output)
            if error:
                print("错误:", error[-500:] if len(error) > 500 else error)
        
        print("\n部署到Nginx...")
        stdin, stdout, stderr = ssh.exec_command("""
            mkdir -p /var/www/frontend && \
            rm -rf /var/www/frontend/* && \
            cp -r /opt/ai-novel-media-agent/frontend/dist/* /var/www/frontend/ && \
            chown -R www-data:www-data /var/www/frontend && \
            ls -la /var/www/frontend/
        """)
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n配置Nginx...")
        nginx_config = """
server {
    listen 8000;
    server_name _;
    root /var/www/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:9000/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/etc/nginx/sites-available/user-frontend', 'w') as f:
            f.write(nginx_config)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("""
            ln -sf /etc/nginx/sites-available/user-frontend /etc/nginx/sites-enabled/ && \
            nginx -t && \
            systemctl reload nginx
        """)
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n测试访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:8000/")
        stdout.channel.recv_exit_status()
        status = stdout.read().decode('utf-8')
        print(f"用户端: {status}")
        
        if '200' in status:
            print("\n✓ 用户端部署成功!")
            print("访问地址: http://104.244.90.202:8000")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
