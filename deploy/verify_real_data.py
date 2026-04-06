#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证Dashboard真实数据"""

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
        
        print("=" * 60)
        print("1. 检查数据库真实数据")
        print("=" * 60)
        
        check_db = """
import sqlite3
conn = sqlite3.connect('/opt/ai-novel-media-agent/backend/data/app.db')
cursor = conn.cursor()

print("\n数据库统计:")
cursor.execute("SELECT COUNT(*) FROM users")
print(f"  用户总数: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('pending', 'running')")
print(f"  活跃任务: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
print(f"  排队任务: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM novels")
novels = cursor.fetchone()[0]
print(f"  小说总数: {novels}")

cursor.execute("SELECT COUNT(*) FROM videos")
videos = cursor.fetchone()[0]
print(f"  视频总数: {videos}")
print(f"  作品总数: {novels + videos}")

conn.close()
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/check_real_db.py', 'w') as f:
            f.write(check_db)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/check_real_db.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n" + "=" * 60)
        print("2. 检查后端API返回")
        print("=" * 60)
        
        test_api = """
import requests
import json

response = requests.get('http://localhost:9000/api/admin/dashboard')
if response.status_code == 200:
    data = response.json()
    print("\nAPI返回数据:")
    print(f"  用户总数: {data['total_users']}")
    print(f"  活跃任务: {data['active_tasks']}")
    print(f"  排队任务: {data['queued_tasks']}")
    print(f"  小说总数: {data['total_novels']}")
    print(f"  视频总数: {data['total_videos']}")
    print(f"  作品总数: {data['total_novels'] + data['total_videos']}")
else:
    print(f"API错误: {response.status_code}")
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/test_api.py', 'w') as f:
            f.write(test_api)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("python3 /tmp/test_api.py")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n" + "=" * 60)
        print("3. 测试外部访问API")
        print("=" * 60)
        
        stdin, stdout, stderr = ssh.exec_command("curl -s http://104.244.90.202:9000/api/admin/dashboard")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        
        import json
        try:
            data = json.loads(output)
            print("\n外部API返回:")
            print(f"  用户总数: {data['total_users']}")
            print(f"  活跃任务: {data['active_tasks']}")
            print(f"  排队任务: {data['queued_tasks']}")
            print(f"  小说总数: {data['total_novels']}")
            print(f"  视频总数: {data['total_videos']}")
            print(f"  作品总数: {data['total_novels'] + data['total_videos']}")
        except:
            print(f"解析失败: {output}")
        
        print("\n" + "=" * 60)
        print("4. 检查管理端前端文件")
        print("=" * 60)
        
        stdin, stdout, stderr = ssh.exec_command("stat /var/www/admin/index.html | grep Modify")
        stdout.channel.recv_exit_status()
        print(f"\n前端构建时间: {stdout.read().decode('utf-8')}")
        
        print("\n" + "=" * 60)
        print("结论")
        print("=" * 60)
        print("\n如果数据库、API都返回正确数据(0)，但浏览器显示错误数据(89, 45000)，")
        print("说明是浏览器缓存问题。")
        print("\n解决方法:")
        print("1. 按 Ctrl+Shift+Delete 清除浏览器缓存")
        print("2. 或按 Ctrl+Shift+R 强制刷新")
        print("3. 或使用无痕模式访问 http://104.244.90.202/admin")
        
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
