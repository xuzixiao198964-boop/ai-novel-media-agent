#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查Dashboard API返回的数据"""

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
        
        print("检查Dashboard API返回的数据...")
        
        test_script = """
import requests
import json

response = requests.get('http://localhost:9000/api/admin/dashboard/stats')
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("返回数据:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print(f"错误: {response.text}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/check_dashboard.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/check_dashboard.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查数据库实际数据...")
        check_db = """
import sqlite3
conn = sqlite3.connect('/opt/ai-novel-media-agent/backend/data/app.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM users")
print(f"用户总数: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM tasks")
print(f"任务总数: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM novels")
print(f"小说总数: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM videos")
print(f"视频总数: {cursor.fetchone()[0]}")

conn.close()
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/check_db.py', 'w') as f:
            f.write(check_db)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/check_db.py")
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
