#!/usr/bin/env python3
"""完整重新部署脚本"""
import os
import sys
import time
import paramiko
from scp import SCPClient

# 服务器配置
SERVER = "104.244.90.202"
USER = "root"
PASSWORD = "8TbXfNYaywmW"

# 全局SSH客户端
ssh_client = None

def get_ssh_client():
    """获取SSH客户端"""
    global ssh_client
    if ssh_client is None:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(SERVER, username=USER, password=PASSWORD, timeout=30)
    return ssh_client

def run_ssh_command(command, check=True):
    """执行SSH命令"""
    print(f"\n执行: {command}")
    client = get_ssh_client()
    stdin, stdout, stderr = client.exec_command(command)

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_code = stdout.channel.recv_exit_status()

    if output:
        print(output)
    if error:
        print(error, file=sys.stderr)

    if check and exit_code != 0:
        raise Exception(f"命令执行失败 (exit code {exit_code}): {command}")

    return output, error, exit_code

def upload_file(local_path, remote_path):
    """上传文件"""
    print(f"\n上传: {local_path} -> {remote_path}")
    client = get_ssh_client()

    with SCPClient(client.get_transport()) as scp:
        scp.put(local_path, remote_path, recursive=True)

    print("上传成功")

def main():
    print("=" * 60)
    print("开始完整重新部署")
    print("=" * 60)

    # 1. 测试SSH连接
    print("\n[1/8] 测试SSH连接...")
    try:
        run_ssh_command("echo 'SSH连接成功'")
    except Exception as e:
        print(f"SSH连接失败: {e}")
        print("\n请检查:")
        print("1. 服务器IP是否正确: 104.244.90.202")
        print("2. SSH密码是否正确")
        print("3. 服务器SSH服务是否运行")
        return

    # 2. 备份现有数据
    print("\n[2/8] 备份数据库...")
    run_ssh_command("sudo -u postgres pg_dump ai_novel_media > /tmp/backup.sql 2>/dev/null || echo '数据库不存在，跳过备份'", check=False)

    # 3. 停止现有服务
    print("\n[3/8] 停止现有服务...")
    run_ssh_command("systemctl stop ai-novel-api 2>/dev/null || true", check=False)
    run_ssh_command("systemctl stop nginx 2>/dev/null || true", check=False)

    # 4. 清理旧文件
    print("\n[4/8] 清理旧文件...")
    run_ssh_command("rm -rf /opt/ai-novel-media-agent")
    run_ssh_command("mkdir -p /opt/ai-novel-media-agent")

    # 5. 上传后端代码
    print("\n[5/8] 上传后端代码...")
    backend_dir = "E:/work/ai-novel-media-agent/backend"
    upload_file(backend_dir, "/opt/ai-novel-media-agent/")

    # 6. 安装依赖和配置数据库
    print("\n[6/8] 安装依赖和配置数据库...")
    commands = [
        "cd /opt/ai-novel-media-agent/backend",
        "python3 -m pip install --upgrade pip",
        "pip3 install -r requirements.txt",
        # 配置PostgreSQL
        "sudo -u postgres psql -c \"DROP DATABASE IF EXISTS ai_novel_media;\"",
        "sudo -u postgres psql -c \"CREATE DATABASE ai_novel_media;\"",
        "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE ai_novel_media TO ai_novel;\"",
        "sudo -u postgres psql -d ai_novel_media -c \"GRANT ALL ON SCHEMA public TO ai_novel;\"",
        # 初始化数据库
        "cd /opt/ai-novel-media-agent/backend && python3 -c 'from app.database import Base, engine; Base.metadata.create_all(bind=engine); print(\"数据库表创建成功\")'",
    ]
    for cmd in commands:
        run_ssh_command(cmd)

    # 7. 配置systemd服务
    print("\n[7/8] 配置systemd服务...")
    service_content = """[Unit]
Description=AI Novel Media Agent API
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-novel-media-agent/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="DATABASE_URL=postgresql://ai_novel:ai_novel_pass@localhost/ai_novel_media"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    # 写入服务文件
    run_ssh_command(f"cat > /etc/systemd/system/ai-novel-api.service << 'EOF'\n{service_content}\nEOF")
    run_ssh_command("systemctl daemon-reload")
    run_ssh_command("systemctl enable ai-novel-api")
    run_ssh_command("systemctl start ai-novel-api")

    # 8. 上传和配置前端
    print("\n[8/8] 部署前端应用...")

    # 上传官网
    upload_file("E:/work/ai-novel-media-agent/official-site", "/tmp/")
    run_ssh_command("rm -rf /var/www/html && mkdir -p /var/www/html")
    run_ssh_command("cp -r /tmp/official-site/* /var/www/html/")

    # 上传用户端
    upload_file("E:/work/ai-novel-media-agent/frontend/dist", "/tmp/frontend-dist")
    run_ssh_command("mkdir -p /var/www/html/app")
    run_ssh_command("cp -r /tmp/frontend-dist/* /var/www/html/app/")

    # 上传管理后台
    upload_file("E:/work/ai-novel-media-agent/admin/dist", "/tmp/admin-dist")
    run_ssh_command("mkdir -p /var/www/html/admin")
    run_ssh_command("cp -r /tmp/admin-dist/* /var/www/html/admin/")

    # 配置Nginx
    nginx_conf = """server {
    listen 80;
    server_name _;

    # 官网
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 用户端应用
    location /app {
        alias /var/www/html/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    # 管理后台
    location /admin {
        alias /var/www/html/admin;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:9000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:9000/docs;
        proxy_set_header Host $host;
    }
}
"""

    run_ssh_command(f"cat > /etc/nginx/sites-available/default << 'EOF'\n{nginx_conf}\nEOF")
    run_ssh_command("nginx -t")
    run_ssh_command("systemctl start nginx")
    run_ssh_command("systemctl enable nginx")

    # 等待服务启动
    print("\n等待服务启动...")
    time.sleep(5)

    # 检查服务状态
    print("\n检查服务状态...")
    run_ssh_command("systemctl status ai-novel-api --no-pager", check=False)
    run_ssh_command("systemctl status nginx --no-pager", check=False)

    print("\n" + "=" * 60)
    print("部署完成！")
    print("=" * 60)
    print("\n访问地址:")
    print(f"  官网: http://{SERVER}/")
    print(f"  用户端: http://{SERVER}/app/")
    print(f"  管理后台: http://{SERVER}/admin/")
    print(f"  API文档: http://{SERVER}/docs")
    print("\n测试账号: 15606537209 / 198964")
    print("管理员账号: admin / admin123")

    # 关闭SSH连接
    if ssh_client:
        ssh_client.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n部署失败: {e}", file=sys.stderr)
        if ssh_client:
            ssh_client.close()
        sys.exit(1)
