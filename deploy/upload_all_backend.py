#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "104.244.90.202"
USER = "root"
PASSWORD = "vDyCuc83NxWw"

def upload_core_files():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到服务器 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASSWORD)

        sftp = ssh.open_sftp()

        # 上传security.py
        print("上传security.py...")
        local_file = r"E:\work\ai-novel-media-agent\backend\app\core\security.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/core/security.py"
        sftp.put(local_file, remote_file)
        print("✓ security.py上传成功")

        # 上传deps.py
        print("上传deps.py...")
        local_file = r"E:\work\ai-novel-media-agent\backend\app\core\deps.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/core/deps.py"
        sftp.put(local_file, remote_file)
        print("✓ deps.py上传成功")

        # 上传users.py
        print("上传users.py...")
        local_file = r"E:\work\ai-novel-media-agent\backend\app\api\users.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/api/users.py"
        sftp.put(local_file, remote_file)
        print("✓ users.py上传成功")

        # 上传payments.py
        print("上传payments.py...")
        local_file = r"E:\work\ai-novel-media-agent\backend\app\api\payments.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/api/payments.py"
        sftp.put(local_file, remote_file)
        print("✓ payments.py上传成功")

        # 上传main.py
        print("上传main.py...")
        local_file = r"E:\work\ai-novel-media-agent\backend\app\main.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/main.py"
        sftp.put(local_file, remote_file)
        print("✓ main.py上传成功")

        sftp.close()

        # 重启后端服务
        print("\n重启后端服务...")
        commands = [
            "pkill -f 'uvicorn app.main:app' || true",
            "sleep 2",
            "cd /opt/ai-novel-media-agent/backend && nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/backend.log 2>&1 &",
            "sleep 3"
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()

        print("✓ 后端服务已重启")

        # 检查服务状态
        print("\n检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        ps_result = stdout.read().decode()

        if ps_result:
            print("✓ 后端服务运行中")
        else:
            print("✗ 后端服务未运行")
            print("\n查看错误日志:")
            stdin, stdout, stderr = ssh.exec_command("tail -50 /var/log/backend.log")
            log = stdout.read().decode()
            print(log)
            return

        # 测试健康检查
        import time
        time.sleep(2)
        print("\n测试健康检查...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/health")
        health = stdout.read().decode()
        print(f"健康检查: {health}")

        print("\n✓ 部署完成！")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_core_files()
