#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全新环境完整部署脚本"""

import paramiko
import time
import sys
import io
import os
import tarfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(ssh, command, description="", timeout=300, ignore_error=False):
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
        if error and exit_status != 0 and not ignore_error:
            print(f"错误: {error}")

        return exit_status, output, error
    except Exception as e:
        print(f"命令执行异常: {e}")
        if not ignore_error:
            raise
        return -1, "", str(e)

def main():
    host = "104.244.90.202"
    username = "root"
    password = "vDyCuc83NxWw"
    project_dir = "E:/work/ai-novel-media-agent"

    print(f"开始部署到全新服务器 {host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接服务器
        print(f"\n连接到服务器 {host}...")
        ssh.connect(host, 22, username, password, timeout=30, banner_timeout=60)
        print("SSH连接成功\n")

        # 1. 更新系统并安装基础软件
        run_command(ssh, "apt-get update", "更新软件源", 300)
        run_command(ssh,
            "DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx curl tar",
            "安装基础软件", 600)

        # 2. 创建项目目录
        run_command(ssh, "mkdir -p /opt/ai-novel-media-agent", "创建项目目录", 10)

        # 3. 打包并上传项目文件
        print("\n" + "="*60)
        print("打包项目文件")
        print("="*60)

        tar_path = f"{project_dir}/deploy_package.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(f"{project_dir}/backend", arcname="backend")
            tar.add(f"{project_dir}/official-site", arcname="official-site")
            tar.add(f"{project_dir}/frontend/dist", arcname="frontend/dist")
        print(f"打包完成: {tar_path}")

        print("\n" + "="*60)
        print("上传项目文件")
        print("="*60)
        sftp = ssh.open_sftp()
        sftp.put(tar_path, "/opt/ai-novel-media-agent/deploy_package.tar.gz")
        sftp.close()
        print("上传完成")

        # 4. 解压项目文件
        run_command(ssh,
            "cd /opt/ai-novel-media-agent && tar -xzf deploy_package.tar.gz && rm deploy_package.tar.gz",
            "解压项目文件", 60)

        # 5. 安装Python依赖
        run_command(ssh,
            "cd /opt/ai-novel-media-agent/backend && pip3 install --break-system-packages -r requirements.txt",
            "安装Python依赖", 600)

        # 6. 配置PostgreSQL
        run_command(ssh, "systemctl start postgresql", "启动PostgreSQL", 30)
        run_command(ssh, "systemctl enable postgresql", "设置PostgreSQL开机启动", 10)

        run_command(ssh,
            """sudo -u postgres psql -c "CREATE DATABASE ai_novel_media;" """,
            "创建数据库", 30, ignore_error=True)

        run_command(ssh,
            """sudo -u postgres psql -c "CREATE USER ai_novel WITH PASSWORD 'ai_novel_pass';" """,
            "创建数据库用户", 30, ignore_error=True)

        run_command(ssh,
            """sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_novel_media TO ai_novel;" """,
            "授予数据库权限", 30)

        # 7. 创建.env文件
        env_content = """DATABASE_URL=postgresql://ai_novel:ai_novel_pass@localhost/ai_novel_media
SECRET_KEY=your-secret-key-change-in-production
DEEPSEEK_API_KEY=your-deepseek-api-key
CORS_ORIGINS=*
FRONTEND_URL=http://104.244.90.202:8000
BACKEND_URL=http://104.244.90.202:9000
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com
"""

        print("\n" + "="*60)
        print("创建环境配置文件")
        print("="*60)
        sftp = ssh.open_sftp()
        with sftp.open('/opt/ai-novel-media-agent/backend/.env', 'w') as f:
            f.write(env_content)
        sftp.close()
        print("配置文件已创建")

        # 8. 初始化数据库
        run_command(ssh,
            "cd /opt/ai-novel-media-agent/backend && python3 -c 'from app.database import init_db; init_db()'",
            "初始化数据库", 60)

        # 9. 创建systemd服务
        service_content = """[Unit]
Description=AI Novel Media Agent Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-novel-media-agent/backend
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

        print("\n" + "="*60)
        print("创建systemd服务")
        print("="*60)
        sftp = ssh.open_sftp()
        with sftp.open('/etc/systemd/system/ai-novel-media-agent.service', 'w') as f:
            f.write(service_content)
        sftp.close()
        print("服务文件已创建")

        # 10. 启动后端服务
        run_command(ssh, "systemctl daemon-reload", "重载systemd", 10)
        run_command(ssh, "systemctl enable ai-novel-media-agent", "设置服务开机启动", 10)
        run_command(ssh, "systemctl start ai-novel-media-agent", "启动后端服务", 30)
        time.sleep(5)
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查服务状态", 10)

        # 11. 配置Nginx
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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

        print("\n" + "="*60)
        print("配置Nginx")
        print("="*60)
        sftp = ssh.open_sftp()
        with sftp.open('/etc/nginx/sites-available/ai-novel-media-agent', 'w') as f:
            f.write(nginx_config)
        sftp.close()
        print("Nginx配置已创建")

        run_command(ssh, "rm -f /etc/nginx/sites-enabled/default", "删除默认配置", 10, ignore_error=True)
        run_command(ssh,
            "ln -sf /etc/nginx/sites-available/ai-novel-media-agent /etc/nginx/sites-enabled/",
            "启用配置", 10)
        run_command(ssh, "nginx -t", "测试Nginx配置", 10)
        run_command(ssh, "systemctl restart nginx", "重启Nginx", 30)

        # 12. 测试系统
        print("\n" + "="*60)
        print("测试系统")
        print("="*60)

        time.sleep(3)

        run_command(ssh, "curl -s http://localhost/api/health", "健康检查", 10)

        run_command(ssh,
            """curl -s -X POST http://localhost/api/auth/register -H 'Content-Type: application/json' -d '{"username":"15606537209","password":"198964","email":"test@example.com"}'""",
            "注册测试账号", 10)

        run_command(ssh,
            """curl -s -X POST http://localhost/api/auth/login -H 'Content-Type: application/json' -d '{"username":"15606537209","password":"198964"}'""",
            "登录测试", 10)

        # 13. 外部访问测试
        print("\n" + "="*60)
        print("外部访问测试")
        print("="*60)

        import requests

        tests = [
            ("产品官网", f"http://{host}/", "GET", None),
            ("登录页面", f"http://{host}/login.html", "GET", None),
            ("API健康检查", f"http://{host}/api/health", "GET", None),
            ("注册账号", f"http://{host}/api/auth/register", "POST",
             {"username":"testuser","password":"test123","email":"test@test.com"}),
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
                    print(f"OK {name}: {response.status_code}")
                    if 'json' in response.headers.get('content-type', ''):
                        result = response.json()
                        if 'access_token' in result:
                            print(f"  登录成功！Token: {result['access_token'][:30]}...")
                        else:
                            print(f"  {result}")
                    success_count += 1
                elif response.status_code == 400:
                    print(f"OK {name}: {response.status_code} (可能已存在)")
                    success_count += 1
                else:
                    print(f"X {name}: {response.status_code}")
                    print(f"  {response.text[:200]}")
            except Exception as e:
                print(f"X {name}: {e}")

        print("\n" + "="*60)
        print(f"测试完成: {success_count}/{len(tests)} 通过")
        print("="*60)

        if success_count >= 5:
            print("\n" + "="*60)
            print("部署成功！")
            print("="*60)
            print(f"\n访问地址:")
            print(f"  产品官网: http://{host}/")
            print(f"  登录页面: http://{host}/login.html")
            print(f"  用户端应用: http://{host}:8000/")
            print(f"  API文档: http://{host}/docs")
            print(f"\n测试账号: 15606537209 / 198964")
        else:
            print("\n部署未完全成功，请检查日志")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
