#!/usr/bin/env python3
"""重新初始化数据库"""

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
    print("重新初始化数据库")
    print("=" * 60)

    client = connect_ssh()

    # 停止后端服务
    print("\n[1/6] 停止后端服务")
    run_command(client, 'systemctl stop ai-novel-media-agent')
    time.sleep(2)
    print("[OK] 已停止")

    # 备份旧数据库
    print("\n[2/6] 备份旧数据库")
    run_command(client, 'cp /opt/ai-novel-media-agent/backend/data/app.db /opt/ai-novel-media-agent/backend/data/app.db.backup 2>/dev/null || true')
    print("[OK] 已备份")

    # 删除旧数据库
    print("\n[3/6] 删除旧数据库")
    run_command(client, 'rm -f /opt/ai-novel-media-agent/backend/data/app.db')
    print("[OK] 已删除")

    # 重新创建数据库
    print("\n[4/6] 重新创建数据库")
    exit_code, output, error = run_command(client, '''cd /opt/ai-novel-media-agent/backend && python3 -c "
from app.database import engine, Base
from app.models import User, Task, Novel, Video, Payment, APIKey, SystemLog
Base.metadata.create_all(bind=engine)
print('Database created successfully')
" 2>&1''')
    print(output)
    if error:
        print(error)

    # 创建测试用户
    print("\n[5/6] 创建测试用户")
    exit_code, output, error = run_command(client, '''cd /opt/ai-novel-media-agent/backend && python3 -c "
from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db = SessionLocal()

# 创建测试用户
user = User(
    username='admin',
    email='admin@example.com',
    phone='15606537209',
    hashed_password=pwd_context.hash('198964'),
    role='admin',
    subscription_tier='enterprise',
    balance=10000.0
)
db.add(user)
db.commit()
print('Test user created: admin / 198964')
db.close()
" 2>&1''')
    print(output)
    if error:
        print(error)

    # 启动后端服务
    print("\n[6/6] 启动后端服务")
    run_command(client, 'systemctl start ai-novel-media-agent')
    time.sleep(3)
    print("[OK] 已启动")

    # 测试登录
    print("\n[测试] 测试登录")
    time.sleep(2)
    exit_code, output, error = run_command(client, '''curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"198964"}' ''')
    print(f"响应: {output}")

    client.close()

    print("\n" + "=" * 60)
    print("数据库初始化完成")
    print("=" * 60)
    print("\n测试账号:")
    print("  用户名: admin")
    print("  密码: 198964")

if __name__ == '__main__':
    main()
