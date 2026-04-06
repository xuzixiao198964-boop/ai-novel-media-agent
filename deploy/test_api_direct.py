#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接测试API返回"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def execute_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("=" * 70)
    print("直接测试API返回")
    print("=" * 70)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 测试各个API
        print("\n【1】Dashboard统计API")
        print("-" * 70)
        cmd1 = 'curl -s http://localhost:9000/api/admin/dashboard'
        status, output, error = execute_ssh_command(ssh, cmd1)
        print(output)

        print("\n【2】最近用户API")
        print("-" * 70)
        cmd2 = 'curl -s http://localhost:9000/api/admin/dashboard/recent-users?limit=5'
        status, output, error = execute_ssh_command(ssh, cmd2)
        print(output)

        print("\n【3】任务分布API")
        print("-" * 70)
        cmd3 = 'curl -s http://localhost:9000/api/admin/dashboard/task-distribution'
        status, output, error = execute_ssh_command(ssh, cmd3)
        print(output)

        print("\n【4】套餐分布API")
        print("-" * 70)
        cmd4 = 'curl -s http://localhost:9000/api/admin/dashboard/subscription-distribution'
        status, output, error = execute_ssh_command(ssh, cmd4)
        print(output)

        print("\n【5】系统配置API")
        print("-" * 70)
        cmd5 = 'curl -s http://localhost:9000/api/admin/config'
        status, output, error = execute_ssh_command(ssh, cmd5)
        print(output)

        print("\n【6】用户列表API")
        print("-" * 70)
        cmd6 = 'curl -s http://localhost:9000/api/admin/users'
        status, output, error = execute_ssh_command(ssh, cmd6)
        print(output)

        ssh.close()

        print("\n" + "=" * 70)
        print("测试完成")
        print("=" * 70)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
