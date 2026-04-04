#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""强制清理缓存并重启后端"""
import paramiko
import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

    print("[Step 1] Killing all backend processes...")
    stdin, stdout, stderr = ssh.exec_command("pkill -9 -f 'uvicorn.*9000'")
    stdout.channel.recv_exit_status()
    time.sleep(2)
    print("  [OK] All processes killed")

    print("[Step 2] Clearing Python cache...")
    stdin, stdout, stderr = ssh.exec_command("""
cd /opt/ai-novel-media-agent/backend
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
""")
    stdout.channel.recv_exit_status()
    print("  [OK] Cache cleared")

    print("[Step 3] Starting backend...")
    command = """
cd /opt/ai-novel-media-agent/backend && \
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload > /var/log/ai-novel-backend.log 2>&1 &
"""
    stdin, stdout, stderr = ssh.exec_command(command)
    stdout.channel.recv_exit_status()
    print("  [OK] Backend started with --reload")

    print("[Step 4] Waiting for startup...")
    time.sleep(5)

    print("[Step 5] Testing API...")
    import requests

    # 登录
    login_resp = requests.post("http://104.244.90.202/api/auth/login",
                              json={"username": "15606537209", "password": "198964"})
    token = login_resp.json().get("access_token")

    # 测试novels
    response = requests.get("http://104.244.90.202/api/novels",
                           headers={"Authorization": f"Bearer {token}"},
                           timeout=10)
    print(f"  Novels API: {response.status_code}")
    if response.status_code == 200:
        print(f"  Response: {response.json()}")

    # 测试videos
    response = requests.get("http://104.244.90.202/api/videos",
                           headers={"Authorization": f"Bearer {token}"},
                           timeout=10)
    print(f"  Videos API: {response.status_code}")

    print("\n[SUCCESS] Backend restarted with fresh cache!")

finally:
    ssh.close()
