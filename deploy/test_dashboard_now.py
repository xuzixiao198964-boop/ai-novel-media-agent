#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试Dashboard API"""

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
        
        test_script = """
import requests
import json

print("测试Dashboard API...")
response = requests.get('http://localhost:9000/api/admin/dashboard')
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("\n返回数据:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print("\n数据验证:")
    print(f"✓ 用户总数: {data['total_users']}")
    print(f"✓ 活跃任务: {data['active_tasks']}")
    print(f"✓ 排队任务: {data['queued_tasks']}")
    print(f"✓ 小说总数: {data['total_novels']}")
    print(f"✓ 视频总数: {data['total_videos']}")
    print(f"✓ 作品总数: {data['total_novels'] + data['total_videos']}")
    print(f"✓ 今日收入: ¥{data['today_income']}")
else:
    print(f"✗ 失败: {response.text}")

print("\n测试其他Dashboard接口...")
response = requests.get('http://localhost:9000/api/admin/dashboard/task-distribution')
print(f"任务分布: {response.status_code}")

response = requests.get('http://localhost:9000/api/admin/dashboard/subscription-distribution')
print(f"套餐分布: {response.status_code}")

response = requests.get('http://localhost:9000/api/admin/dashboard/income-trend?days=7')
print(f"收入趋势: {response.status_code}")

response = requests.get('http://localhost:9000/api/admin/dashboard/recent-users?limit=5')
print(f"最近用户: {response.status_code}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_dash.py', 'w') as f:
            f.write(test_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_dash.py")
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
