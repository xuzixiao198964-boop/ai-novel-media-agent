#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重启后端服务"""
import paramiko
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

def restart_backend():
    print("[Deploy] Restarting backend service...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"[SSH] Connecting to {SERVER_IP}...")
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

        # 查找并杀死旧进程
        print("[Step 1] Finding backend process...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'uvicorn.*9000' | grep -v grep")
        output = stdout.read().decode()
        print(output if output else "  No process found")

        if output:
            print("[Step 2] Killing old process...")
            stdin, stdout, stderr = ssh.exec_command("pkill -f 'uvicorn.*9000'")
            stdout.channel.recv_exit_status()
            print("  [OK] Old process killed")

        # 启动新进程
        print("[Step 3] Starting new backend process...")
        command = """
cd /opt/ai-novel-media-agent/backend && \
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/ai-novel-backend.log 2>&1 &
"""
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout.channel.recv_exit_status()
        print("  [OK] New process started")

        # 等待启动
        import time
        print("[Step 4] Waiting for service to start...")
        time.sleep(3)

        # 验证服务
        print("[Step 5] Verifying service...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'uvicorn.*9000' | grep -v grep")
        output = stdout.read().decode()

        if output:
            print("  [OK] Backend is running")
            print(f"  Process: {output.strip()}")
        else:
            print("  [ERROR] Backend not running")
            return False

        # 测试API
        print("[Step 6] Testing API...")
        import requests

        try:
            response = requests.get("http://104.244.90.202/api/health", timeout=10)
            if response.status_code == 200:
                print("  [OK] API is responding")
                return True
            else:
                print(f"  [WARN] API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"  [ERROR] API test failed: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] Restart failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    restart_backend()
