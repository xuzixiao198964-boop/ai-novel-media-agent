#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查前端部署"""

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
        
        print("检查管理端前端文件...")
        stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/admin/assets/*.js | head -5")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查前端构建时间...")
        stdin, stdout, stderr = ssh.exec_command("stat /var/www/admin/index.html | grep Modify")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n测试外部访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w 'HTTP %{http_code}' http://104.244.90.202/admin/")
        stdout.channel.recv_exit_status()
        print(f"管理端: {stdout.read().decode('utf-8')}")
        
        stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w 'HTTP %{http_code}' http://104.244.90.202:9000/api/admin/dashboard")
        stdout.channel.recv_exit_status()
        print(f"Dashboard API: {stdout.read().decode('utf-8')}")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
