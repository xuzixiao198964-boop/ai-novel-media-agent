#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查服务启动问题"""

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
        
        print("检查systemd服务日志...")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u ai-novel-backend -n 50 --no-pager")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n手动启动服务...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/manual_start.log 2>&1 &")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(3)
        
        print("\n检查进程...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print(output if output else "没有找到uvicorn进程")
        
        print("\n检查启动日志...")
        stdin, stdout, stderr = ssh.exec_command("cat /tmp/manual_start.log")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n测试登录...")
        test_script = """
import requests
try:
    response = requests.post(
        'http://localhost:9000/api/auth/login',
        json={'username': 'admin', 'password': '198964'},
        timeout=5
    )
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 登录成功!")
    else:
        print(f"✗ 失败: {response.text}")
except Exception as e:
    print(f"✗ 连接失败: {e}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_login3.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_login3.py")
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
