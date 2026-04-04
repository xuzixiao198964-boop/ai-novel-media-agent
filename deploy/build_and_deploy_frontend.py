#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建并部署前端项目
"""
import paramiko
import os
import tarfile
import sys

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "8TbXfNYaywmW"

def exec_cmd(ssh, cmd, desc=""):
    if desc:
        print(f"  {desc}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    if exit_status != 0 and err:
        print(f"    [WARN] {err[:200]}")
    return out, err

def main():
    print("="*60)
    print("构建并部署前端项目")
    print("="*60)

    # 步骤1: 本地构建前端
    print("\n步骤1: 本地构建前端项目")

    os.chdir("E:/work/ai-novel-media-agent")

    # 构建用户端
    print("  构建用户端...")
    os.chdir("frontend")
    os.system("npm install --legacy-peer-deps > nul 2>&1")
    ret = os.system("npm run build")
    if ret != 0:
        print("    [ERROR] 用户端构建失败")
        return 1
    print("    [OK] 用户端构建成功")

    # 构建管理后台
    print("  构建管理后台...")
    os.chdir("../admin")
    os.system("npm install --legacy-peer-deps > nul 2>&1")
    ret = os.system("npm run build")
    if ret != 0:
        print("    [ERROR] 管理后台构建失败")
        return 1
    print("    [OK] 管理后台构建成功")

    os.chdir("..")

    # 步骤2: 打包前端文件
    print("\n步骤2: 打包前端文件")
    tar_path = "frontend_dist.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add("frontend/dist", arcname="frontend/dist")
        tar.add("admin/dist", arcname="admin/dist")
        tar.add("official-site", arcname="official-site")
    print(f"  [OK] 打包完成: {tar_path}")

    # 步骤3: 上传到服务器
    print("\n步骤3: 上传到服务器")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, 22, SERVER_USER, SERVER_PASSWORD, timeout=30)
    print("  [OK] SSH连接成功")

    sftp = ssh.open_sftp()
    remote_tar = f"/tmp/{tar_path}"
    sftp.put(tar_path, remote_tar)
    sftp.close()
    print(f"  [OK] 上传完成: {remote_tar}")

    # 步骤4: 解压并部署
    print("\n步骤4: 解压并部署")
    exec_cmd(ssh, f"cd /opt/ai-novel-media-agent && tar -xzf {remote_tar}", "解压文件")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/frontend/dist", "设置frontend权限")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/admin/dist", "设置admin权限")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/official-site", "设置官网权限")
    print("  [OK] 部署完成")

    # 步骤5: 更新官网到 /var/www/html
    print("\n步骤5: 更新官网")
    exec_cmd(ssh, "cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/", "复制官网文件")
    exec_cmd(ssh, "chmod -R 755 /var/www/html", "设置权限")
    print("  [OK] 官网更新完成")

    # 步骤6: 配置Nginx
    print("\n步骤6: 配置Nginx")
    nginx_config = """server {
    listen 80;
    server_name _;

    root /var/www/html;
    index index.html;

    # 产品官网
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 用户端 - 独立端口
server {
    listen 8000;
    server_name _;

    root /opt/ai-novel-media-agent/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 管理后台 - 独立端口
server {
    listen 8001;
    server_name _;

    root /opt/ai-novel-media-agent/admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}"""

    exec_cmd(ssh, f"cat > /etc/nginx/sites-available/default << 'EOF'\n{nginx_config}\nEOF", "写入配置")
    out, err = exec_cmd(ssh, "nginx -t", "测试配置")
    print(out + err)
    exec_cmd(ssh, "systemctl reload nginx", "重载Nginx")
    print("  [OK] Nginx配置完成")

    ssh.close()

    # 步骤7: 验证
    print("\n步骤7: 验证所有服务")
    import requests
    import time
    time.sleep(3)

    tests = [
        ("产品官网", "http://104.244.90.202/"),
        ("用户端", "http://104.244.90.202:8000/"),
        ("管理后台", "http://104.244.90.202:8001/"),
        ("后端API", "http://104.244.90.202:9000/api/health"),
    ]

    passed = 0
    for name, url in tests:
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                print(f"  [OK] {name}: 成功")
                passed += 1
            else:
                print(f"  [FAIL] {name}: {resp.status_code}")
        except Exception as e:
            print(f"  [FAIL] {name}: {str(e)[:50]}")

    print("\n" + "="*60)
    print(f"验证结果: {passed}/{len(tests)} 通过")
    print("="*60)
    print("\n✅ 所有访问地址：")
    print("  产品官网: http://104.244.90.202/")
    print("  用户端: http://104.244.90.202:8000/")
    print("  管理后台: http://104.244.90.202:8001/")
    print("  API文档: http://104.244.90.202:9000/docs")

    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
