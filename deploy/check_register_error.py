#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看注册错误日志"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(ssh, command, description="", timeout=30):
    """执行SSH命令"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print('='*60)

    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()

        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')

        if output:
            print(output)
        if error and exit_status != 0:
            print(f"错误: {error}")

        return exit_status, output, error
    except Exception as e:
        print(f"命令执行异常: {e}")
        return -1, "", str(e)

def main():
    host = "104.244.90.202"
    username = "root"
    password = "vDyCuc83NxWw"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, 22, username, password, timeout=30, banner_timeout=60)

        # 查看详细日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 50 --no-pager | grep -A 20 'Internal Server Error'", "查看错误日志", 10)

        # 尝试注册并立即查看日志
        print("\n尝试注册...")
        run_command(ssh,
            """curl -s -X POST http://localhost:9000/api/auth/register -H 'Content-Type: application/json' -d '{"username":"testuser2","password":"test123","email":"test2@example.com"}'""",
            "注册测试", 10)

        import time
        time.sleep(2)

        run_command(ssh, "journalctl -u ai-novel-media-agent -n 30 --no-pager", "查看最新日志", 10)

    except Exception as e:
        print(f"错误: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
