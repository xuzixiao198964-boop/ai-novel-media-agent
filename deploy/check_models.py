#!/usr/bin/env python3
"""检查服务器上的模型定义"""
import paramiko

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"
PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"连接服务器 {SERVER}...")
    ssh.connect(SERVER, port=PORT, username=USERNAME, password=PASSWORD)

    # 读取服务器上的models.py
    cmd = "cat /opt/ai-novel-media-agent/backend/app/models.py | head -80"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

except Exception as e:
    print(f"错误: {e}")
finally:
    ssh.close()
