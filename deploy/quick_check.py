#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速检查并启动后端"""

import paramiko
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_ssh_command(ssh, command, timeout=30):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("连接服务器...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD, timeout=10)
        print("✓ 已连接")

        # 1. 检查端口
        print("\n1. 检查9000端口...")
        status, output, error = run_ssh_command(ssh, "lsof -i:9000 || echo 'Port 9000 is free'")
        print(output)

        # 2. 杀死旧进程
        print("\n2. 清理旧进程...")
        run_ssh_command(ssh, "pkill -9 -f 'uvicorn app.main:app'")
        time.sleep(2)
        print("✓ 已清理")

        # 3. 启动后端
        print("\n3. 启动后端服务...")
        run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/backend && \
            nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &
        """)

        print("等待5秒...")
        time.sleep(5)

        # 4. 测试
        print("\n4. 测试API...")
        status, output, error = run_ssh_command(ssh, "curl -s http://localhost:9000/api/health")

        if "healthy" in output:
            print("✓ 后端服务正常")
            print(output)
        else:
            print("✗ 后端服务异常")
            print("输出:", output)
            print("\n查看日志:")
            status, log, _ = run_ssh_command(ssh, "tail -50 /tmp/backend.log")
            print(log)

        # 5. 测试登录
        print("\n5. 测试登录...")
        status, output, error = run_ssh_command(ssh, """
            curl -s -X POST http://localhost:9000/api/auth/login \
                -H "Content-Type: application/json" \
                -d '{"username":"admin","password":"198964"}'
        """)

        if "access_token" in output:
            print("✓ 登录成功")
        else:
            print("✗ 登录失败")
            print(output)

        # 6. 测试用户API
        print("\n6. 测试用户管理API...")
        status, output, error = run_ssh_command(ssh, "curl -s 'http://localhost:9000/api/admin/users?skip=0&limit=10'")

        if "password" in output and "198964" in output:
            print("✓ 用户管理API正常（包含明文密码）")
        else:
            print("✗ 用户管理API异常")
            print(output[:200])

        print("\n" + "="*60)
        print("部署状态检查完成")
        print("="*60)

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
