#!/usr/bin/env python3
"""快速测试脚本 - 只上传pytest.ini并运行测试"""

import paramiko
import sys
import time

# 服务器配置
SERVER = {
    'host': '104.244.90.202',
    'port': 22,
    'username': 'root',
    'password': 'vDyCuc83NxWw'
}

def connect_ssh():
    """连接到服务器"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SERVER['host'],
        port=SERVER['port'],
        username=SERVER['username'],
        password=SERVER['password']
    )
    return client

def run_command(client, command, show_output=True):
    """执行SSH命令"""
    stdin, stdout, stderr = client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if show_output:
        if output:
            print(output)
        if error:
            print(error, file=sys.stderr)

    return exit_code, output, error

def main():
    print("=" * 60)
    print("快速测试 - 更新pytest.ini并运行测试")
    print("=" * 60)

    # 连接服务器
    print("\n[1/4] 连接到服务器")
    client = connect_ssh()
    sftp = client.open_sftp()
    print("[OK] 已连接")

    # 上传pytest.ini
    print("\n[2/4] 上传pytest.ini")
    sftp.put('pytest.ini', '/opt/ai-novel-media-agent/pytest.ini')
    print("[OK] 已上传")

    # 运行单元测试
    print("\n[3/4] 运行单元测试")
    print("-" * 60)
    exit_code, output, error = run_command(
        client,
        'cd /opt/ai-novel-media-agent && PYTHONPATH=/opt/ai-novel-media-agent/backend python3 -m pytest backend/tests/unit/ -v',
        show_output=True
    )

    if exit_code == 0:
        print("[OK] 单元测试通过")
    else:
        print("[FAIL] 单元测试失败")

    # 运行集成测试
    print("\n[4/4] 运行集成测试")
    print("-" * 60)
    exit_code, output, error = run_command(
        client,
        'cd /opt/ai-novel-media-agent && PYTHONPATH=/opt/ai-novel-media-agent/backend python3 -m pytest backend/tests/integration/ -v',
        show_output=True
    )

    if exit_code == 0:
        print("[OK] 集成测试通过")
    else:
        print("[FAIL] 集成测试失败")

    # 清理
    sftp.close()
    client.close()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
