#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Nginx配置和完整测试"""

import paramiko
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(ssh, command, description="", timeout=30):
    """执行SSH命令"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print('='*60)

    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()

        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')

        if output:
            print(output)
        if error and exit_status != 0:
            print(f"错误: {error}")

        return exit_status, output, error
    except Exception as e:
        print(f"命令执行异常: {e}")
        return -1, "", str(e)

def main():
    host = "104.244.90.202"
    username = "root"
    password = "8TbXfNYaywmW"

    print(f"连接到服务器 {host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, 22, username, password, timeout=30)
        print("SSH连接成功\n")

        # 1. 查看当前Nginx配置
        run_command(ssh, "cat /etc/nginx/sites-enabled/default", "查看Nginx配置", 10)

        # 2. 停止所有9000端口进程
        run_command(ssh, "lsof -ti:9000 | xargs kill -9 || true", "停止9000端口进程", 10)
        time.sleep(2)

        # 3. 创建正确的Nginx配置
        nginx_config = """server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # 产品官网
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 用户端应用 (8000端口)
    location /app {
        alias /var/www/html/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    # 后端API (通过80端口的/api路径访问)
    location /api/ {
        proxy_pass http://127.0.0.1:9000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}

# 8000端口 - 用户端应用
server {
    listen 8000;
    listen [::]:8000;
    server_name _;

    root /var/www/html/app;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:9000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""

        # 4. 写入Nginx配置
        stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-enabled/default")
        stdin.write(nginx_config)
        stdin.channel.shutdown_write()
        stdout.channel.recv_exit_status()
        print("Nginx配置已更新")

        # 5. 测试Nginx配置
        run_command(ssh, "nginx -t", "测试Nginx配置", 10)

        # 6. 重启Nginx
        run_command(ssh, "systemctl restart nginx", "重启Nginx", 10)

        # 7. 重启后端服务
        run_command(ssh, "systemctl restart ai-novel-media-agent", "重启后端服务", 10)
        time.sleep(5)

        # 8. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查后端状态", 10)
        run_command(ssh, "systemctl status nginx --no-pager", "检查Nginx状态", 10)

        # 9. 测试API
        print("\n" + "="*60)
        print("测试后端API")
        print("="*60)

        run_command(ssh, "curl -s http://localhost:9000/health", "直接访问9000端口", 10)
        run_command(ssh, "curl -s http://localhost/api/health", "通过Nginx访问API", 10)

        # 10. 创建测试账号
        run_command(ssh,
            "curl -s -X POST http://localhost/api/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\",\"email\":\"test@example.com\"}'",
            "注册测试账号", 10)

        # 11. 测试登录
        run_command(ssh,
            "curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\"}'",
            "登录测试", 10)

        # 12. 外部访问测试
        print("\n" + "="*60)
        print("外部访问测试")
        print("="*60)

        import requests

        tests = [
            ("产品官网", f"http://{host}/", "GET", None),
            ("登录页面", f"http://{host}/login.html", "GET", None),
            ("用户端应用", f"http://{host}:8000/", "GET", None),
            ("API健康检查", f"http://{host}/api/health", "GET", None),
            ("注册账号", f"http://{host}/api/auth/register", "POST",
             {"username":"15606537209","password":"198964","email":"test@example.com"}),
            ("登录", f"http://{host}/api/auth/login", "POST",
             {"username":"15606537209","password":"198964"}),
        ]

        for name, url, method, data in tests:
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)

                status = "✓" if response.status_code in [200, 201] else "✗"
                print(f"{status} {name}: {response.status_code}")
                if response.status_code not in [200, 201]:
                    print(f"  响应: {response.text[:200]}")
            except Exception as e:
                print(f"✗ {name}: {e}")

        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
        print("\n访问地址:")
        print(f"  产品官网: http://{host}/")
        print(f"  用户端应用: http://{host}:8000/")
        print(f"  测试账号: 15606537209 / 198964")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
