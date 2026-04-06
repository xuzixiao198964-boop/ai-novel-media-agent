#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import os
import sys
import io

# 设置输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 服务器信息
HOST = "104.244.90.202"
USER = "root"
PASSWORD = "vDyCuc83NxWw"

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到服务器 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASSWORD)

        # 上传main.py
        print("上传main.py...")
        sftp = ssh.open_sftp()
        local_file = r"E:\work\ai-novel-media-agent\backend\app\main.py"
        remote_file = "/opt/ai-novel-media-agent/backend/app/main.py"
        sftp.put(local_file, remote_file)
        sftp.close()
        print("✓ main.py上传成功")

        # 重启后端服务
        print("\n重启后端服务...")
        commands = [
            "cd /opt/ai-novel-media-agent/backend",
            "pkill -f 'uvicorn app.main:app' || true",
            "sleep 2",
            "nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/backend.log 2>&1 &",
            "sleep 3"
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read()

        print("✓ 后端服务已重启")

        # 测试API
        print("\n测试API端点...")
        test_commands = [
            "curl -s http://localhost:9000/api/health",
            "curl -s -H 'Authorization: Bearer test' http://localhost:9000/api/users/profile || echo 'Need auth'",
            "curl -s -H 'Authorization: Bearer test' http://localhost:9000/api/payments/history || echo 'Need auth'"
        ]

        for cmd in test_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode()
            print(f"  {cmd.split('/')[-1]}: {result[:100]}")

        print("\n✓ 部署完成！")
        print("\n访问地址:")
        print(f"  用户端: http://{HOST}:8000")
        print(f"  管理端: http://{HOST}/admin")
        print(f"  API文档: http://{HOST}:9000/docs")

    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
