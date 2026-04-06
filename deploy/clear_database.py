#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清空数据库，只保留admin账户"""

import paramiko
import sys
import io

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_ssh_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("=" * 60)
    print("清空数据库，只保留admin账户")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接到服务器 {SERVER}...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("✓ 连接成功")

        # 创建清空数据库的Python脚本
        clear_script = """
import sqlite3
import bcrypt

# 连接数据库
conn = sqlite3.connect('/opt/ai-novel-media-agent/backend/data/app.db')
cursor = conn.cursor()

# 删除所有表的数据（除了admin用户）
print("清空数据表...")

# 删除关联表数据
cursor.execute("DELETE FROM payments")
cursor.execute("DELETE FROM api_keys")
cursor.execute("DELETE FROM publish_records")
cursor.execute("DELETE FROM system_logs")
cursor.execute("DELETE FROM videos")
cursor.execute("DELETE FROM novels")
cursor.execute("DELETE FROM tasks")

# 删除非admin用户
cursor.execute("DELETE FROM users WHERE username != 'admin'")

# 确保admin用户存在且密码正确
cursor.execute("SELECT id FROM users WHERE username = 'admin'")
admin = cursor.fetchone()

if admin:
    # 更新admin密码为198964
    hashed = bcrypt.hashpw('198964'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "UPDATE users SET hashed_password = ?, email = ?, is_active = 1, balance = 0.0, subscription_tier = 'enterprise' WHERE username = 'admin'",
        (hashed, 'admin@example.com')
    )
    print("✓ 更新admin用户密码")
else:
    # 创建admin用户
    hashed = bcrypt.hashpw('198964'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, role, subscription_tier, balance, is_active) VALUES (?, ?, ?, ?, ?, ?, ?)",
        ('admin', 'admin@example.com', hashed, 'admin', 'enterprise', 0.0, 1)
    )
    print("✓ 创建admin用户")

conn.commit()
conn.close()

print("✓ 数据库清空完成，只保留admin账户")
print("  用户名: admin")
print("  密码: 198964")
"""

        print("\n上传清空脚本...")
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/clear_db.py', 'w') as f:
            f.write(clear_script)
        sftp.close()
        print("✓ 脚本上传成功")

        print("\n执行清空脚本...")
        status, output, error = run_ssh_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 /tmp/clear_db.py")

        if output:
            print(output)
        if error:
            print(f"错误: {error}")

        if status == 0:
            print("\n✓ 数据库清空成功")
        else:
            print(f"\n✗ 清空失败，退出码: {status}")
            return 1

        # 验证数据
        print("\n验证数据库...")
        verify_script = """
import sqlite3
conn = sqlite3.connect('/opt/ai-novel-media-agent/backend/data/app.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"用户数: {user_count}")

cursor.execute("SELECT COUNT(*) FROM tasks")
task_count = cursor.fetchone()[0]
print(f"任务数: {task_count}")

cursor.execute("SELECT COUNT(*) FROM novels")
novel_count = cursor.fetchone()[0]
print(f"小说数: {novel_count}")

cursor.execute("SELECT COUNT(*) FROM videos")
video_count = cursor.fetchone()[0]
print(f"视频数: {video_count}")

cursor.execute("SELECT username, email, role, subscription_tier FROM users")
users = cursor.fetchall()
print(f"\\n用户列表:")
for u in users:
    print(f"  - {u[0]} ({u[1]}) - {u[2]} - {u[3]}")

conn.close()
"""

        sftp = ssh.open_sftp()
        with sftp.file('/tmp/verify_db.py', 'w') as f:
            f.write(verify_script)
        sftp.close()

        status, output, error = run_ssh_command(ssh, "cd /opt/ai-novel-media-agent/backend && python3 /tmp/verify_db.py")

        if output:
            print(output)

        print("\n" + "=" * 60)
        print("数据库清空完成")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
