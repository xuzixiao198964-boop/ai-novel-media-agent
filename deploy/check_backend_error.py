#!/usr/bin/env python3
"""检查后端错误日志"""

import paramiko
import sys

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
    print("检查后端错误")
    print("=" * 60)

    client = connect_ssh()

    # 检查环境变量
    print("\n[1] 检查环境变量:")
    exit_code, output, error = run_command(client, 'cat /opt/ai-novel-media-agent/backend/.env')
    print(output)

    # 检查数据库连接
    print("\n[2] 检查数据库连接:")
    exit_code, output, error = run_command(client, 'systemctl status postgresql')
    if 'active (running)' in output:
        print("[OK] PostgreSQL 运行正常")
    else:
        print("[FAIL] PostgreSQL 未运行")
        print(output)

    # 检查 Redis 连接
    print("\n[3] 检查 Redis 连接:")
    exit_code, output, error = run_command(client, 'systemctl status redis')
    if 'active (running)' in output:
        print("[OK] Redis 运行正常")
    else:
        print("[FAIL] Redis 未运行")
        print(output)

    # 查看最近的错误日志
    print("\n[4] 查看最近的错误日志:")
    exit_code, output, error = run_command(client, 'journalctl -u ai-novel-media-agent -n 50 --no-pager | grep -i error')
    print(output)

    # 测试数据库连接
    print("\n[5] 测试数据库连接:")
    exit_code, output, error = run_command(client, '''cd /opt/ai-novel-media-agent/backend && python3 -c "from app.database import engine; print('Database connection OK')" 2>&1''')
    print(output)

    # 检查用户表
    print("\n[6] 检查用户表:")
    exit_code, output, error = run_command(client, '''sudo -u postgres psql -d ai_novel_media -c "SELECT username, phone FROM users LIMIT 5;" 2>&1''')
    print(output)

    client.close()

if __name__ == '__main__':
    main()
