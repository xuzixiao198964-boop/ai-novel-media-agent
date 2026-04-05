#!/usr/bin/env python3
"""检查服务状态"""

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
    print("检查服务状态")
    print("=" * 60)

    client = connect_ssh()

    # 检查后端服务状态
    print("\n[1] 后端服务状态:")
    exit_code, output, error = run_command(client, 'systemctl status ai-novel-media-agent')
    print(output)
    if error:
        print(error)

    # 检查端口监听
    print("\n[2] 端口监听状态:")
    exit_code, output, error = run_command(client, 'netstat -tlnp | grep -E ":(80|9000)"')
    print(output)

    # 检查最近的日志
    print("\n[3] 最近的服务日志:")
    exit_code, output, error = run_command(client, 'journalctl -u ai-novel-media-agent -n 50 --no-pager')
    print(output)

    # 检查 Nginx 状态
    print("\n[4] Nginx 状态:")
    exit_code, output, error = run_command(client, 'systemctl status nginx')
    print(output)

    # 测试本地访问
    print("\n[5] 本地访问测试:")
    exit_code, output, error = run_command(client, 'curl -s http://localhost:9000/api/health')
    print(f"健康检查: {output}")

    client.close()

if __name__ == '__main__':
    main()
