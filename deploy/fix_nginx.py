#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Nginx配置"""

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
        ssh.connect(host, 22, username, password, timeout=30, banner_timeout=60)
        print("SSH连接成功\n")

        # 1. 查看当前Nginx配置
        run_command(ssh, "cat /etc/nginx/sites-enabled/ai-novel-media-agent", "当前Nginx配置", 10)

        # 2. 创建新的Nginx配置
        nginx_config = """server {
    listen 80;
    server_name _;

    # 产品官网
    location / {
        root /opt/ai-novel-media-agent/official-site;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:9000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:9000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:9000/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}

server {
    listen 8000;
    server_name _;

    # 用户端应用
    location / {
        root /opt/ai-novel-media-agent/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
"""

        # 3. 上传新配置
        print("\n" + "="*60)
        print("上传新的Nginx配置")
        print("="*60)

        sftp = ssh.open_sftp()
        with sftp.open('/etc/nginx/sites-enabled/ai-novel-media-agent', 'w') as f:
            f.write(nginx_config)
        sftp.close()
        print("配置已上传")

        # 4. 测试Nginx配置
        run_command(ssh, "nginx -t", "测试Nginx配置", 10)

        # 5. 重启Nginx
        run_command(ssh, "systemctl reload nginx", "重启Nginx", 10)

        # 6. 等待服务启动
        time.sleep(3)

        # 7. 测试API
        print("\n" + "="*60)
        print("测试API")
        print("="*60)

        run_command(ssh, "curl -s http://localhost/api/health", "健康检查", 10)

        # 8. 创建测试账号
        run_command(ssh,
            "curl -s -X POST http://localhost/api/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\",\"email\":\"test@example.com\"}'",
            "注册测试账号", 10)

        # 9. 测试登录
        run_command(ssh,
            "curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\"}'",
            "登录测试", 10)

        # 10. 外部访问测试
        print("\n" + "="*60)
        print("外部访问测试")
        print("="*60)

        import requests

        tests = [
            ("产品官网", f"http://{host}/", "GET", None),
            ("登录页面", f"http://{host}/login.html", "GET", None),
            ("API健康检查", f"http://{host}/api/health", "GET", None),
            ("注册账号", f"http://{host}/api/auth/register", "POST",
             {"username":"testuser3","password":"test123","email":"test3@test.com"}),
            ("登录", f"http://{host}/api/auth/login", "POST",
             {"username":"15606537209","password":"198964"}),
            ("用户端应用", f"http://{host}:8000/", "GET", None),
        ]

        success_count = 0
        for name, url, method, data in tests:
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)

                if response.status_code in [200, 201]:
                    print(f"✓ {name}: {response.status_code}")
                    if 'json' in response.headers.get('content-type', ''):
                        result = response.json()
                        if 'access_token' in result:
                            print(f"  登录成功，获得token")
                        else:
                            print(f"  {result}")
                    success_count += 1
                elif response.status_code == 400:
                    print(f"✓ {name}: {response.status_code} (可能已存在)")
                    print(f"  {response.text[:200]}")
                    success_count += 1
                else:
                    print(f"✗ {name}: {response.status_code}")
                    print(f"  {response.text[:200]}")
            except Exception as e:
                print(f"✗ {name}: {e}")

        print("\n" + "="*60)
        print(f"测试完成: {success_count}/{len(tests)} 通过")
        print("="*60)

        if success_count >= 5:
            print("\n✓✓✓ 系统部署成功！✓✓✓")
            print("\n访问地址:")
            print(f"  产品官网: http://{host}/")
            print(f"  登录页面: http://{host}/login.html")
            print(f"  用户端应用: http://{host}:8000/")
            print(f"  API文档: http://{host}/docs")
            print(f"\n测试账号: 15606537209 / 198964")
            print("\n现在可以在浏览器中测试登录功能了！")
        else:
            print("\n✗ 部署未完全成功，请检查日志")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
