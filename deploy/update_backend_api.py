#!/usr/bin/env python3
"""更新后端代码到服务器"""
import paramiko
import os

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"
PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"连接服务器 {SERVER}...")
    ssh.connect(SERVER, port=PORT, username=USERNAME, password=PASSWORD)

    sftp = ssh.open_sftp()

    # 上传更新的文件
    print("上传 main.py...")
    sftp.put("E:/work/ai-novel-media-agent/backend/app/main.py",
             "/opt/ai-novel-media-agent/backend/app/main.py")

    print("上传 admin_simple.py...")
    sftp.put("E:/work/ai-novel-media-agent/backend/app/api/admin_simple.py",
             "/opt/ai-novel-media-agent/backend/app/api/admin_simple.py")

    sftp.close()

    # 重启后端服务
    print("重启后端服务...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-novel-backend")
    stdout.channel.recv_exit_status()

    print("\n[OK] 后端更新完成！")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
