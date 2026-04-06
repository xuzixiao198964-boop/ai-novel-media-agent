#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查用户端前端"""

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
        
        print("检查用户端前端构建时间...")
        stdin, stdout, stderr = ssh.exec_command("stat /var/www/frontend/index.html 2>/dev/null | grep Modify || echo '文件不存在'")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查Nginx配置...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 10 'listen 8000' /etc/nginx/sites-available/ai-novel 2>/dev/null || echo '未找到8000端口配置'")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
