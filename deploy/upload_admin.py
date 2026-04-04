#!/usr/bin/env python3
import paramiko
import time

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

def upload_admin():
    print("上传管理后台文件...")

    # 重试连接
    for i in range(3):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
            break
        except Exception as e:
            print(f"连接失败 (尝试 {i+1}/3): {e}")
            if i < 2:
                time.sleep(5)
            else:
                raise

    sftp = ssh.open_sftp()

    # 上传文件
    print("上传 admin-dist.tar.gz...")
    sftp.put("E:/work/ai-novel-media-agent/admin/admin-dist.tar.gz", "/tmp/admin-dist.tar.gz")

    # 解压并部署
    print("解压并部署...")
    commands = [
        "mkdir -p /var/www/admin",
        "cd /var/www/admin && tar -xzf /tmp/admin-dist.tar.gz",
        "chown -R www-data:www-data /var/www/admin",
        "chmod -R 755 /var/www/admin",
        "rm /tmp/admin-dist.tar.gz"
    ]

    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
        print(f"OK: {cmd}")

    # 更新Nginx配置
    print("更新Nginx配置...")
    nginx_config = """server {
    listen 80;
    server_name _;

    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /app {
        alias /var/www/app;
        index index.html;
        try_files $uri $uri/ /app/index.html;
    }

    location /admin {
        alias /var/www/admin;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://127.0.0.1:9000/docs;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:9000/openapi.json;
    }
}
"""

    stdin, stdout, stderr = ssh.exec_command("cat > /etc/nginx/sites-available/default")
    stdin.write(nginx_config)
    stdin.channel.shutdown_write()

    # 重启Nginx
    print("重启Nginx...")
    stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl restart nginx")
    print(stdout.read().decode())

    sftp.close()
    ssh.close()

    print("\n=== 管理后台部署完成！ ===")
    print(f"访问地址: http://{SERVER_IP}/admin/")

if __name__ == "__main__":
    upload_admin()
