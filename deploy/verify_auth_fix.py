#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证auth.py是否正确更新"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        
        print("检查服务器上的auth.py...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 2 'def verify_password' /opt/ai-novel-media-agent/backend/app/api/auth.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查服务进程...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n强制杀死旧进程并重启...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f uvicorn && sleep 2 && systemctl start ai-novel-backend")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(3)
        
        print("\n检查新进程...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n再次测试登录...")
        test_script = """
import requests
response = requests.post(
    'http://localhost:9000/api/auth/login',
    json={'username': 'admin', 'password': '198964'}
)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("✓ 登录成功!")
    print(f"Token: {response.json()['access_token'][:50]}...")
else:
    print(f"✗ 失败: {response.text}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_login2.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_login2.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
