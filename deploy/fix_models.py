#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上传models.py并重启后端"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("[Deploy] Uploading models.py...")
    ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

    sftp = ssh.open_sftp()
    sftp.put("E:/work/ai-novel-media-agent/backend/app/models.py",
             "/opt/ai-novel-media-agent/backend/app/models.py")
    print("  [OK] models.py uploaded")
    sftp.close()

    # 重启后端
    print("[Deploy] Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command("pkill -f 'uvicorn.*9000'")
    stdout.channel.recv_exit_status()

    command = """
cd /opt/ai-novel-media-agent/backend && \
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/ai-novel-backend.log 2>&1 &
"""
    stdin, stdout, stderr = ssh.exec_command(command)
    stdout.channel.recv_exit_status()
    print("  [OK] Backend restarted")

    # 等待启动
    import time
    time.sleep(5)

    # 测试
    print("[Deploy] Testing API...")
    import requests
    response = requests.get("http://104.244.90.202/api/health", timeout=10)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  [OK] Backend is working!")
    else:
        print("  [ERROR] Backend not responding correctly")

finally:
    ssh.close()
