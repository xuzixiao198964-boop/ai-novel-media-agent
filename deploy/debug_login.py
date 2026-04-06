#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试登录问题"""

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
        
        print("检查数据库中的用户信息...")
        
        check_script = """
import sqlite3
import bcrypt

conn = sqlite3.connect('/opt/ai-novel-media-agent/backend/data/app.db')
cursor = conn.cursor()

cursor.execute("SELECT username, hashed_password FROM users WHERE username = 'admin'")
user = cursor.fetchone()

if user:
    print(f"用户名: {user[0]}")
    print(f"密码哈希: {user[1][:50]}...")
    
    # 测试密码验证
    try:
        result = bcrypt.checkpw('198964'.encode('utf-8'), user[1].encode('utf-8'))
        print(f"密码验证结果: {result}")
    except Exception as e:
        print(f"密码验证错误: {e}")
else:
    print("未找到admin用户")

conn.close()
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/check_user.py', 'w') as f:
            f.write(check_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && python3 /tmp/check_user.py")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print(output)
        if error:
            print("错误:", error)
        
        # 检查auth.py的verify_password函数
        print("\n检查auth.py...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 5 'def verify_password' /opt/ai-novel-media-agent/backend/app/api/auth.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
