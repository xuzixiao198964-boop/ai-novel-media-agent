#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库表结构并清空数据"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def execute_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("检查数据库表结构...")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 检查users表结构
        check_script = """
cd /opt/ai-novel-media-agent/backend
sqlite3 data/app.db << 'EOFSQL'
.schema users
EOFSQL
"""
        status, output, error = execute_ssh_command(ssh, check_script)
        print("Users表结构:")
        print(output)

        # 清空数据，使用正确的字段
        clear_script = """
cd /opt/ai-novel-media-agent/backend

python3 << 'EOFPYTHON'
import sqlite3
import hashlib

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

print("开始清空数据...")

# 清空所有表
tables = ['novels', 'videos', 'tasks', 'api_keys', 'system_logs', 'publish_records', 'payments']
for table in tables:
    cursor.execute(f"DELETE FROM {table}")
    print(f"清空 {table}: {cursor.rowcount} 条")

# 清空用户表，保留管理员
cursor.execute("DELETE FROM users WHERE username NOT IN ('admin', '15606537209')")
print(f"清空 users: {cursor.rowcount} 条（保留管理员）")

# 确保管理员账户存在
admin_password = "198964"
hashed = hashlib.sha256(admin_password.encode()).hexdigest()

# 获取users表的所有列
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Users表字段: {columns}")

# 根据实际字段构建SQL
if 'is_admin' in columns:
    cursor.execute("INSERT OR REPLACE INTO users (id, username, email, hashed_password, is_active, is_admin, balance, subscription_tier, created_at) VALUES (1, 'admin', 'admin@example.com', ?, 1, 1, 0.0, 'enterprise', datetime('now'))", (hashed,))
    cursor.execute("INSERT OR REPLACE INTO users (id, username, phone, email, hashed_password, is_active, is_admin, balance, subscription_tier, created_at) VALUES (2, '15606537209', '15606537209', '15606537209@example.com', ?, 1, 1, 0.0, 'enterprise', datetime('now'))", (hashed,))
else:
    cursor.execute("INSERT OR REPLACE INTO users (id, username, email, hashed_password, is_active, balance, subscription_tier, created_at) VALUES (1, 'admin', 'admin@example.com', ?, 1, 0.0, 'enterprise', datetime('now'))", (hashed,))
    cursor.execute("INSERT OR REPLACE INTO users (id, username, phone, email, hashed_password, is_active, balance, subscription_tier, created_at) VALUES (2, '15606537209', '15606537209', '15606537209@example.com', ?, 1, 0.0, 'enterprise', datetime('now'))", (hashed,))

print("管理员账户已确认")

conn.commit()
conn.close()

print("数据清空完成！")
EOFPYTHON
"""

        print("\n清空数据...")
        status, output, error = execute_ssh_command(ssh, clear_script)
        print(output)
        if error:
            print(f"错误: {error}")

        # 验证
        verify_script = """
cd /opt/ai-novel-media-agent/backend
sqlite3 data/app.db << 'EOFSQL'
.mode column
.headers on
SELECT id, username, phone, email, balance, subscription_tier FROM users;
EOFSQL
"""
        status, output, error = execute_ssh_command(ssh, verify_script)
        print("\n当前用户:")
        print(output)

        ssh.close()

        print("\n完成！保留账户: admin/198964, 15606537209/198964")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
