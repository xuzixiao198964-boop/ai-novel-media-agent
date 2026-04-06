#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查服务器上的代码"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        
        print("检查服务器上的admin_simple.py...")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'def get_dashboard_stats' /opt/ai-novel-media-agent/backend/app/api/admin_simple.py")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        
        if output:
            print("找到Dashboard API:")
            print(output)
        else:
            print("未找到Dashboard API，需要上传最新代码")
        
        print("\n检查路由注册...")
        stdin, stdout, stderr = ssh.exec_command("grep -n 'dashboard' /opt/ai-novel-media-agent/backend/app/api/admin_simple.py | head -20")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
