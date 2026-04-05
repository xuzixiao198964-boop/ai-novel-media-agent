#!/usr/bin/env python3
"""使用Python直接操作SQLite数据库创建用户"""

import paramiko
import sys
import hashlib

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def main():
    print("=" * 60)
    print("使用Python直接创建用户")
    print("=" * 60)

    try:
        # 连接服务器
        print("\n[1/4] 连接服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("[OK] 已连接")

        # 停止后端服务
        print("\n[2/4] 停止后端服务")
        run_command(ssh, "systemctl stop ai-novel-media-agent")
        print("[OK] 已停止")

        # 使用Python创建用户
        print("\n[3/4] 创建用户")
        password_hash = hashlib.sha256("198964".encode()).hexdigest()

        create_script = f"""
python3 << 'PYEOF'
import sqlite3
from datetime import datetime

db_path = '/opt/ai-novel-media-agent/backend/data/app.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 删除已存在的用户
cursor.execute("DELETE FROM users WHERE username IN ('admin', '15606537209')")

# 创建管理员用户
now = datetime.utcnow().isoformat()
sql = "INSERT INTO users (username, email, phone, hashed_password, role, subscription_tier, balance, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
cursor.execute(sql, ('admin', 'admin@example.com', '15606537209', '{password_hash}', 'admin', 'premium', 1000.0, 1, now, now))

# 创建手机号用户
cursor.execute(sql, ('15606537209', '15606537209@example.com', '15606537209', '{password_hash}', 'admin', 'premium', 1000.0, 1, now, now))

conn.commit()

# 验证
cursor.execute("SELECT id, username, email, phone, role FROM users WHERE username IN ('admin', '15606537209')")
users = cursor.fetchall()
print("创建的用户:")
for user in users:
    print(f"  ID: {{user[0]}}, Username: {{user[1]}}, Email: {{user[2]}}, Phone: {{user[3]}}, Role: {{user[4]}}")

conn.close()
print("\\n用户创建成功！")
PYEOF
"""
        stdout, stderr = run_command(ssh, create_script)
        print(stdout)
        if stderr:
            print(f"[WARNING] {stderr}")

        # 启动后端服务
        print("\n[4/4] 启动后端服务")
        run_command(ssh, "systemctl start ai-novel-media-agent")
        import time
        time.sleep(3)
        stdout, stderr = run_command(ssh, "systemctl status ai-novel-media-agent")
        if "active (running)" in stdout:
            print("[OK] 服务已启动")
        else:
            print("[WARNING] 服务状态异常")

        # 测试登录
        print("\n[5/4] 测试登录")
        test_commands = [
            ('admin', 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\''),
            ('15606537209', 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"15606537209","password":"198964"}\''),
        ]

        for name, cmd in test_commands:
            stdout, stderr = run_command(ssh, cmd)
            if '"access_token"' in stdout:
                print(f"\n[OK] {name} 登录成功")
            else:
                print(f"\n[FAIL] {name} 登录失败: {stdout[:200]}")

        ssh.close()

        print("\n" + "=" * 60)
        print("用户创建完成")
        print("=" * 60)
        print("\n登录信息:")
        print("  用户名: admin 或 15606537209")
        print("  密码: 198964")
        print("  URL: http://104.244.90.202/admin")
        print("\n请在浏览器中测试登录！")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
