#!/usr/bin/env python3
"""创建测试用户（使用简单密码哈希）"""

import paramiko
import sys
import time

SERVER = {
    'host': '104.244.90.202',
    'port': 22,
    'username': 'root',
    'password': 'vDyCuc83NxWw'
}

def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SERVER['host'],
        port=SERVER['port'],
        username=SERVER['username'],
        password=SERVER['password']
    )
    return client

def run_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_code, output, error

def main():
    print("=" * 60)
    print("创建测试用户")
    print("=" * 60)

    client = connect_ssh()

    # 停止后端服务
    print("\n[1/4] 停止后端服务")
    run_command(client, 'systemctl stop ai-novel-media-agent')
    time.sleep(2)
    print("[OK] 已停止")

    # 创建用户（使用 API 的密码哈希方法）
    print("\n[2/4] 创建测试用户")
    exit_code, output, error = run_command(client, '''cd /opt/ai-novel-media-agent/backend && python3 << 'PYEOF'
from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

db = SessionLocal()

# 删除旧用户
db.query(User).filter(User.username == "admin").delete()
db.query(User).filter(User.phone == "15606537209").delete()
db.commit()

# 创建新用户
user = User(
    username="admin",
    email="admin@example.com",
    phone="15606537209",
    hashed_password=get_password_hash("198964"),
    role="admin",
    subscription_tier="enterprise",
    balance=10000.0
)
db.add(user)
db.commit()
print("User created successfully")
db.close()
PYEOF
''')
    print(output)
    if error:
        print(error)

    # 启动后端服务
    print("\n[3/4] 启动后端服务")
    run_command(client, 'systemctl start ai-novel-media-agent')
    time.sleep(3)
    print("[OK] 已启动")

    # 测试登录
    print("\n[4/4] 测试登录")
    time.sleep(2)

    # 使用 username 登录
    exit_code, output, error = run_command(client, '''curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"198964"}' ''')
    print(f"使用 username 登录: {output}")

    # 使用 phone 登录
    exit_code, output, error = run_command(client, '''curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"15606537209","password":"198964"}' ''')
    print(f"使用 phone 登录: {output}")

    client.close()

    print("\n" + "=" * 60)
    print("用户创建完成")
    print("=" * 60)
    print("\n登录信息:")
    print("  用户名: admin 或 15606537209")
    print("  密码: 198964")

if __name__ == '__main__':
    main()
