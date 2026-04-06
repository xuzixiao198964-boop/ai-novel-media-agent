#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复auth.py并重启服务"""

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
        
        print("上传正确的auth.py...")
        sftp = ssh.open_sftp()
        sftp.put('backend/app/api/auth.py', '/opt/ai-novel-media-agent/backend/app/api/auth.py')
        sftp.close()
        print("✓ auth.py上传成功")
        
        print("\n重启后端服务...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart ai-novel-backend")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(2)
        
        print("\n检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status ai-novel-backend | head -10")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n测试登录...")
        test_script = """
import requests
import json

response = requests.post(
    'http://localhost:9000/api/auth/login',
    json={'username': 'admin', 'password': '198964'}
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("✓ 登录成功!")
    data = response.json()
    print(f"Token: {data['access_token'][:50]}...")
else:
    print(f"✗ 登录失败: {response.text}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_login.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_login.py")
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
