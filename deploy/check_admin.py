#!/usr/bin/env python3
"""检查管理后台问题"""

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
    print("检查管理后台问题")
    print("=" * 60)

    client = connect_ssh()

    # 检查管理后台文件
    print("\n[1] 检查管理后台文件:")
    exit_code, output, error = run_command(client, 'ls -lh /opt/ai-novel-media-agent/admin/dist/')
    print(output)

    # 检查 index.html
    print("\n[2] 检查 index.html 内容:")
    exit_code, output, error = run_command(client, 'head -20 /opt/ai-novel-media-agent/admin/dist/index.html')
    print(output)

    # 检查 Nginx 配置
    print("\n[3] 检查 Nginx 配置:")
    exit_code, output, error = run_command(client, 'cat /etc/nginx/sites-available/ai-novel-media-agent | grep -A 10 "location /admin"')
    print(output)

    # 测试 API 登录
    print("\n[4] 测试 API 登录:")
    exit_code, output, error = run_command(client, '''curl -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"15606537209","password":"198964"}' ''')
    print(output)

    # 检查后端日志
    print("\n[5] 检查后端日志:")
    exit_code, output, error = run_command(client, 'journalctl -u ai-novel-media-agent -n 20 --no-pager')
    print(output)

    client.close()

if __name__ == '__main__':
    main()
