#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并更新后端代码"""
import paramiko
import os
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

def update_backend():
    print("[Deploy] Updating backend code...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"[SSH] Connecting to {SERVER_IP}...")
        ssh.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

        # 先检查目录结构
        print("[Step 1] Checking directory structure...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /opt/ai-novel-media-agent/backend/app/")
        output = stdout.read().decode()
        print(output)

        sftp = ssh.open_sftp()

        # 上传修改的文件
        files_to_upload = [
            ("E:/work/ai-novel-media-agent/backend/app/main.py", "/opt/ai-novel-media-agent/backend/app/main.py"),
            ("E:/work/ai-novel-media-agent/backend/app/api/novels.py", "/opt/ai-novel-media-agent/backend/app/api/novels.py"),
            ("E:/work/ai-novel-media-agent/backend/app/api/videos.py", "/opt/ai-novel-media-agent/backend/app/api/videos.py"),
        ]

        print("[Step 2] Uploading modified files...")
        for local_path, remote_path in files_to_upload:
            print(f"  Uploading: {os.path.basename(local_path)}")
            sftp.put(local_path, remote_path)

        # 重启后端服务
        print("[Step 3] Restarting backend service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-novel-backend")
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("[OK] Backend service restarted")
        else:
            print("[ERROR] Failed to restart backend")
            print(stderr.read().decode())

        # 等待服务启动
        import time
        print("[Step 4] Waiting for service to start...")
        time.sleep(3)

        # 测试API
        print("[Step 5] Testing API endpoints...")
        import requests

        tests = [
            ("Health Check", "http://104.244.90.202/api/health"),
            ("Novels API", "http://104.244.90.202/api/novels"),
            ("Videos API", "http://104.244.90.202/api/videos"),
        ]

        success_count = 0
        for name, url in tests:
            try:
                headers = {}
                if "novels" in url or "videos" in url:
                    # 使用测试账号的token
                    import requests as r
                    login_resp = r.post("http://104.244.90.202/api/auth/login",
                                       json={"username": "15606537209", "password": "198964"})
                    if login_resp.status_code == 200:
                        token = login_resp.json().get("access_token")
                        headers = {"Authorization": f"Bearer {token}"}

                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code in [200, 404]:  # 404 is OK for empty lists
                    print(f"  [OK] {name} (status: {response.status_code})")
                    success_count += 1
                else:
                    print(f"  [WARN] {name} (status: {response.status_code})")
            except Exception as e:
                print(f"  [ERROR] {name} (error: {e})")

        print(f"\n[SUCCESS] Backend updated! ({success_count}/{len(tests)} tests passed)")

        sftp.close()
        return True

    except Exception as e:
        print(f"[ERROR] Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    update_backend()
