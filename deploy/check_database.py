#!/usr/bin/env python3
"""检查数据库位置和安装sqlite3"""

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
    print("检查数据库位置")
    print("=" * 60)

    try:
        # 连接服务器
        print("\n[1/5] 连接服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("[OK] 已连接")

        # 查找数据库文件
        print("\n[2/5] 查找数据库文件")
        stdout, stderr = run_command(ssh, "find /opt/ai-novel-media-agent -name '*.db' 2>/dev/null")
        print(f"数据库文件:\n{stdout}")

        # 检查.env配置
        print("\n[3/5] 检查.env配置")
        stdout, stderr = run_command(ssh, "cat /opt/ai-novel-media-agent/.env | grep DATABASE")
        print(f"数据库配置:\n{stdout}")

        # 安装sqlite3
        print("\n[4/5] 安装sqlite3")
        stdout, stderr = run_command(ssh, "apt-get update && apt-get install -y sqlite3")
        if "sqlite3 is already" in stdout or "Setting up sqlite3" in stdout:
            print("[OK] sqlite3已安装")
        else:
            print(stdout[-500:])

        # 检查Python sqlite3模块
        print("\n[5/5] 检查Python sqlite3")
        check_script = """
python3 << 'EOF'
import sqlite3
print("sqlite3 version:", sqlite3.sqlite_version)
EOF
"""
        stdout, stderr = run_command(ssh, check_script)
        print(stdout)

        ssh.close()

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
