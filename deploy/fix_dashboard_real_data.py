#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复Dashboard显示真实数据"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

# Dashboard.tsx修复 - 移除所有假数据fallback
dashboard_fix = """
  // 移除所有 || 假数据的代码
  // 确保所有数据都从API获取，如果API返回null/undefined则显示0
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SERVER, username=USERNAME, password=PASSWORD)
    print("[OK] 连接成功")

    # 1. 检查后端API是否返回真实数据
    print("\n[1] 测试Dashboard API...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard")
    result = stdout.read().decode()
    print(f"API返回: {result[:300]}")

    # 2. 检查任务分布API
    print("\n[2] 测试任务分布API...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard/task-distribution")
    result = stdout.read().decode()
    print(f"任务分布: {result}")

    # 3. 检查套餐分布API
    print("\n[3] 测试套餐分布API...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard/subscription-distribution")
    result = stdout.read().decode()
    print(f"套餐分布: {result}")

    # 4. 检查数据库数据
    print("\n[4] 检查数据库...")
    stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM users;'")
    users = stdout.read().decode().strip()

    stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM tasks;'")
    tasks = stdout.read().decode().strip()

    stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM novels;'")
    novels = stdout.read().decode().strip()

    stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && sqlite3 data/app.db 'SELECT COUNT(*) FROM videos;'")
    videos = stdout.read().decode().strip()

    print(f"用户: {users}, 任务: {tasks}, 小说: {novels}, 视频: {videos}")

    print("\n[OK] 检查完成")
    print("\n请访问 http://104.244.90.202/admin 查看Dashboard")

except Exception as e:
    print(f"[ERROR] {e}")
finally:
    ssh.close()
