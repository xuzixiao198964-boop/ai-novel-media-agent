#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试"""

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
        
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/admin/dashboard")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print("Dashboard API响应:")
        print(output)
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
