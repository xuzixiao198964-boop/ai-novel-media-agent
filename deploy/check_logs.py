#!/usr/bin/env python3
"""检查后端日志"""

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
    print("检查后端日志")
    print("=" * 60)

    try:
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)

        # 查看最近的日志
        print("\n[1/3] 查看systemd日志")
        stdout, stderr = run_command(ssh, "journalctl -u ai-novel-media-agent -n 50 --no-pager")
        print(stdout[-2000:])

        # 测试登录并查看实时日志
        print("\n[2/3] 测试登录")
        run_command(ssh, 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\'')

        import time
        time.sleep(1)

        print("\n[3/3] 查看最新日志")
        stdout, stderr = run_command(ssh, "journalctl -u ai-novel-media-agent -n 20 --no-pager")
        print(stdout)

        ssh.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
