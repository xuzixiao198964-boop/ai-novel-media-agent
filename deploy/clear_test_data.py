#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清空测试数据，只保留管理员账户"""

import paramiko
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 服务器信息
SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def execute_ssh_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("=" * 60)
    print("清空测试数据脚本")
    print("=" * 60)

    try:
        # 连接服务器
        print("\n[1/3] 连接服务器...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)
        print("连接成功")

        # 清空数据库，只保留管理员账户
        print("\n[2/3] 清空数据库测试数据...")

        clear_script = """
cd /opt/ai-novel-media-agent/backend

python3 << 'EOFPYTHON'
import sqlite3
import hashlib

conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()

print("开始清空数据...")

tables_to_clear = ['novels', 'videos', 'tasks', 'api_keys', 'system_logs', 'publish_records', 'payments']

for table in tables_to_clear:
    cursor.execute(f"DELETE FROM {table}")
    count = cursor.rowcount
    print(f"清空 {table} 表: {count} 条记录")

cursor.execute("DELETE FROM users WHERE username NOT IN ('admin', '15606537209')")
deleted_users = cursor.rowcount
print(f"清空 users 表: {deleted_users} 条记录（保留管理员账户）")

admin_password = "198964"
hashed = hashlib.sha256(admin_password.encode()).hexdigest()

cursor.execute("INSERT OR REPLACE INTO users (id, username, email, hashed_password, is_active, is_admin, balance, subscription_tier, created_at) VALUES (1, 'admin', 'admin@example.com', ?, 1, 1, 0.0, 'enterprise', datetime('now'))", (hashed,))

cursor.execute("INSERT OR REPLACE INTO users (id, username, phone, email, hashed_password, is_active, is_admin, balance, subscription_tier, created_at) VALUES (2, '15606537209', '15606537209', '15606537209@example.com', ?, 1, 1, 0.0, 'enterprise', datetime('now'))", (hashed,))

print("管理员账户已确认")

conn.commit()
conn.close()

print("数据清空完成！")
EOFPYTHON
"""

        status, output, error = execute_ssh_command(ssh, clear_script)
        print(output)
        if error:
            print(f"错误信息: {error}")

        # 验证数据
        print("\n[3/3] 验证数据...")
        verify_script = """
cd /opt/ai-novel-media-agent/backend
sqlite3 data/app.db << 'EOFSQL'
.mode column
.headers on
SELECT '=== 用户表 ===' as info;
SELECT id, username, phone, email, is_admin, balance, subscription_tier FROM users;
SELECT '' as info;
SELECT '=== 其他表记录数 ===' as info;
SELECT 'novels' as table_name, COUNT(*) as count FROM novels
UNION ALL
SELECT 'videos', COUNT(*) FROM videos
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'api_keys', COUNT(*) FROM api_keys
UNION ALL
SELECT 'system_logs', COUNT(*) FROM system_logs
UNION ALL
SELECT 'publish_records', COUNT(*) FROM publish_records
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;
EOFSQL
"""
        status, output, error = execute_ssh_command(ssh, verify_script)
        print(output)

        print("\n" + "=" * 60)
        print("✓ 数据清空完成！")
        print("=" * 60)
        print("\n保留的管理员账户:")
        print("  - admin / 198964")
        print("  - 15606537209 / 198964")

        ssh.close()

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
