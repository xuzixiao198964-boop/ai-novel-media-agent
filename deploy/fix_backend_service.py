#!/usr/bin/env python3
"""修复后端服务端口冲突"""

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
    print("修复后端服务")
    print("=" * 60)

    client = connect_ssh()

    # 查找占用 9000 端口的进程
    print("\n[1/5] 查找占用 9000 端口的进程")
    exit_code, output, error = run_command(client, 'lsof -i :9000 | grep LISTEN')
    print(output)

    # 杀掉所有占用 9000 端口的进程
    print("\n[2/5] 停止所有占用 9000 端口的进程")
    run_command(client, 'pkill -9 -f "uvicorn.*9000"')
    run_command(client, 'fuser -k 9000/tcp')
    time.sleep(2)
    print("[OK] 已停止")

    # 停止 systemd 服务
    print("\n[3/5] 停止 systemd 服务")
    run_command(client, 'systemctl stop ai-novel-media-agent')
    time.sleep(2)
    print("[OK] 已停止")

    # 启动 systemd 服务
    print("\n[4/5] 启动 systemd 服务")
    run_command(client, 'systemctl start ai-novel-media-agent')
    time.sleep(3)
    print("[OK] 已启动")

    # 检查服务状态
    print("\n[5/5] 检查服务状态")
    exit_code, output, error = run_command(client, 'systemctl status ai-novel-media-agent')
    if 'active (running)' in output:
        print("[OK] 服务运行正常")
    else:
        print("[FAIL] 服务启动失败")
        print(output)

    # 测试 API
    print("\n[测试] 测试 API 健康检查")
    time.sleep(2)
    exit_code, output, error = run_command(client, 'curl -s http://localhost:9000/api/health')
    print(f"响应: {output}")

    # 测试登录
    print("\n[测试] 测试登录 API")
    exit_code, output, error = run_command(client, '''curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"15606537209","password":"198964"}' ''')
    print(f"响应: {output}")

    client.close()

    print("\n" + "=" * 60)
    print("修复完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
