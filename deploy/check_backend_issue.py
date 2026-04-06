#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查后端启动问题"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_ssh_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)

        print("检查后端启动日志...")
        status, output, error = run_ssh_command(ssh, "tail -100 /tmp/backend.log")
        print(output)
        if error:
            print(f"错误: {error}")

        print("\n检查端口占用...")
        status, output, error = run_ssh_command(ssh, "netstat -tlnp | grep 9000")
        print(output if output else "9000端口未被占用")

        print("\n尝试手动启动后端...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/backend
            python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 2>&1 &
            sleep 5
            curl -s http://localhost:9000/api/health
        """)
        print(output)
        if error:
            print(f"错误: {error}")

        return 0

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
