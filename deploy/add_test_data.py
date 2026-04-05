#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加测试数据到数据库"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 服务器配置
SERVER = '104.244.90.202'
USERNAME = 'root'
PASSWORD = 'vDyCuc83NxWw'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print('=== 连接服务器 ===')
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)
        print('✓ 连接成功')

        # 创建Python脚本添加测试数据
        script = '''
import sqlite3
from datetime import datetime, timedelta
import random

db_path = '/opt/ai-novel-media-agent/backend/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 添加测试用户 ===")
users = [
    ('user1', 'user1@example.com', '15800000001'),
    ('user2', 'user2@example.com', '15800000002'),
    ('user3', 'user3@example.com', '15800000003'),
    ('user4', 'user4@example.com', '15800000004'),
    ('user5', 'user5@example.com', '15800000005'),
]

for username, email, phone in users:
    try:
        cursor.execute("""
            INSERT INTO users (username, email, phone, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, phone, 'dummy_hash', datetime.now().isoformat()))
        print(f"✓ 添加用户: {username}")
    except sqlite3.IntegrityError:
        print(f"- 用户已存在: {username}")

print("\\n=== 添加测试小说 ===")
novels = [
    ('都市修仙传', '都市', 'completed', 150000),
    ('星际争霸录', '科幻', 'in_progress', 80000),
    ('武侠江湖梦', '武侠', 'completed', 200000),
    ('玄幻大陆', '玄幻', 'in_progress', 120000),
    ('悬疑推理案', '悬疑', 'draft', 50000),
]

for title, genre, status, word_count in novels:
    try:
        cursor.execute("""
            INSERT INTO novels (title, genre, status, word_count, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, genre, status, word_count, datetime.now().isoformat()))
        print(f"✓ 添加小说: {title}")
    except sqlite3.IntegrityError:
        print(f"- 小说已存在: {title}")

print("\\n=== 添加测试视频 ===")
videos = [
    ('都市修仙传-第1集', 'completed', 300),
    ('都市修仙传-第2集', 'completed', 280),
    ('星际争霸录-预告片', 'in_progress', 60),
    ('武侠江湖梦-片头曲', 'completed', 120),
    ('玄幻大陆-角色介绍', 'processing', 180),
]

for title, status, duration in videos:
    try:
        cursor.execute("""
            INSERT INTO videos (title, status, duration, created_at)
            VALUES (?, ?, ?, ?)
        """, (title, status, duration, datetime.now().isoformat()))
        print(f"✓ 添加视频: {title}")
    except sqlite3.IntegrityError:
        print(f"- 视频已存在: {title}")

print("\\n=== 添加测试任务 ===")
tasks = [
    ('novel_generation', 'completed', 100),
    ('novel_generation', 'running', 65),
    ('video_generation', 'completed', 100),
    ('video_generation', 'pending', 0),
    ('video_generation', 'failed', 30),
    ('novel_generation', 'running', 45),
    ('video_generation', 'completed', 100),
]

for task_type, status, progress in tasks:
    cursor.execute("""
        INSERT INTO tasks (type, status, progress, created_at)
        VALUES (?, ?, ?, ?)
    """, (task_type, status, progress, datetime.now().isoformat()))
    print(f"✓ 添加任务: {task_type} - {status}")

conn.commit()
conn.close()

print("\\n✓ 测试数据添加完成！")
'''

        print('\n=== 执行数据添加脚本 ===')
        stdin, stdout, stderr = ssh.exec_command(f'cd /opt/ai-novel-media-agent/backend && python3 -c "{script}"')
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')

        print(output)
        if error:
            print('错误输出:', error)

        # 验证数据
        print('\n=== 验证数据 ===')
        stdin, stdout, stderr = ssh.exec_command('cd /opt/ai-novel-media-agent/backend && python3 -c "import sqlite3; conn = sqlite3.connect(\'app.db\'); c = conn.cursor(); print(\'用户数:\', c.execute(\'SELECT COUNT(*) FROM users\').fetchone()[0]); print(\'小说数:\', c.execute(\'SELECT COUNT(*) FROM novels\').fetchone()[0]); print(\'视频数:\', c.execute(\'SELECT COUNT(*) FROM videos\').fetchone()[0]); print(\'任务数:\', c.execute(\'SELECT COUNT(*) FROM tasks\').fetchone()[0])"')
        print(stdout.read().decode('utf-8', errors='ignore'))

        ssh.close()
        print('\n✓ 完成')

    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
