#!/usr/bin/env python3
"""检查auth.py修改并查看日志"""

import paramiko
import sys

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def main():
    print("=" * 60)
    print("检查auth.py修改")
    print("=" * 60)

    try:
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)

        # 查看verify_password函数
        print("\n[1/2] 查看verify_password函数")
        stdout, stderr = run_command(ssh, "grep -A 10 'def verify_password' /opt/ai-novel-media-agent/backend/app/api/auth.py")
        print(stdout)

        # 测试登录并查看日志
        print("\n[2/2] 测试登录并查看日志")
        run_command(ssh, 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\'')

        import time
        time.sleep(1)

        stdout, stderr = run_command(ssh, "journalctl -u ai-novel-media-agent -n 30 --no-pager | tail -20")
        print(stdout)

        ssh.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
