#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新后端代码并重启"""

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
        
        print("上传最新的admin_simple.py...")
        sftp = ssh.open_sftp()
        sftp.put('backend/app/api/admin_simple.py', '/opt/ai-novel-media-agent/backend/app/api/admin_simple.py')
        sftp.close()
        print("✓ 文件上传成功")
        
        print("\n重启后端服务...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f uvicorn && sleep 2 && cd /opt/ai-novel-media-agent/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &")
        stdout.channel.recv_exit_status()
        
        import time
        time.sleep(3)
        
        print("\n检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        if output:
            print("✓ 服务运行正常")
        else:
            print("✗ 服务未启动")
            return 1
        
        print("\n测试Dashboard API...")
        test_script = """
import requests
import json

response = requests.get('http://localhost:9000/api/admin/dashboard')
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("✓ Dashboard API正常")
    print(f"  用户总数: {data['total_users']}")
    print(f"  活跃任务: {data['active_tasks']}")
    print(f"  排队任务: {data['queued_tasks']}")
    print(f"  小说总数: {data['total_novels']}")
    print(f"  视频总数: {data['total_videos']}")
    print(f"  今日收入: ¥{data['today_income']}")
else:
    print(f"✗ 失败: {response.text}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_dashboard.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_dashboard.py")
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
