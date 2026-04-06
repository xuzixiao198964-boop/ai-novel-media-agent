#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并修复部署问题"""

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
    print("检查部署问题...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)

        # 检查后端日志
        print("\n1. 检查后端日志...")
        status, output, error = run_ssh_command(ssh, "tail -50 /tmp/backend.log")
        print(output)
        if error:
            print(f"错误: {error}")

        # 检查后端进程
        print("\n2. 检查后端进程...")
        status, output, error = run_ssh_command(ssh, "ps aux | grep uvicorn | grep -v grep")
        print(output if output else "后端进程未运行")

        # 重启后端
        print("\n3. 重启后端服务...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/backend
            pkill -9 -f "uvicorn app.main:app"
            sleep 2
            nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &
            sleep 5
            ps aux | grep uvicorn | grep -v grep
        """)
        print(output)

        # 测试后端
        print("\n4. 测试后端API...")
        status, output, error = run_ssh_command(ssh, """
            curl -s http://localhost:9000/api/health
            echo ""
            curl -s -X POST http://localhost:9000/api/auth/login \
                -H "Content-Type: application/json" \
                -d '{"username":"admin","password":"198964"}'
        """)
        print(output)

        # 检查用户端前端构建错误
        print("\n5. 检查用户端前端构建...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/frontend
            npm run build 2>&1 | tail -30
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
