#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底修复前端部署问题
"""
import paramiko
import sys

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "8TbXfNYaywmW"

def exec_cmd(ssh, cmd, desc=""):
    if desc:
        print(f"  {desc}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')

def main():
    print("="*60)
    print("诊断并修复前端部署问题")
    print("="*60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, 22, SERVER_USER, SERVER_PASSWORD, timeout=30)
    print("[OK] SSH连接成功\n")

    # 步骤1: 检查构建目录
    print("步骤1: 检查构建目录")
    out, _ = exec_cmd(ssh, "ls -la /opt/ai-novel-media-agent/frontend/dist/ 2>&1 | head -10", "检查frontend/dist")
    print(out)

    out, _ = exec_cmd(ssh, "ls -la /opt/ai-novel-media-agent/admin/dist/ 2>&1 | head -10", "检查admin/dist")
    print(out)

    # 步骤2: 检查Nginx错误日志
    print("\n步骤2: 检查Nginx错误日志")
    out, _ = exec_cmd(ssh, "tail -20 /var/log/nginx/error.log", "查看错误日志")
    print(out[:500])

    # 步骤3: 修复方案 - 使用proxy_pass而不是alias
    print("\n步骤3: 使用简化的Nginx配置")

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
}"""

    exec_cmd(ssh, f"cat > /etc/nginx/sites-available/default << 'EOF'\n{nginx_config}\nEOF", "写入新配置")

    # 步骤4: 测试并重载Nginx
    print("\n步骤4: 测试并重载Nginx")
    out, err = exec_cmd(ssh, "nginx -t", "测试配置")
    print(out + err)

    exec_cmd(ssh, "systemctl reload nginx", "重载Nginx")
    print("[OK] Nginx已重载")

    # 步骤5: 设置文件权限
    print("\n步骤5: 设置文件权限")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/frontend/dist", "设置frontend权限")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/admin/dist", "设置admin权限")
    print("[OK] 权限已设置")

    ssh.close()

    # 步骤6: 验证
    print("\n步骤6: 验证所有服务")
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
    print("\n访问地址：")
    print("  产品官网: http://104.244.90.202/")
    print("  用户端: http://104.244.90.202:8000/")
    print("  管理后台: http://104.244.90.202:8001/")
    print("  API文档: http://104.244.90.202:9000/docs")

    return 0 if passed == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main())
