#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证8000端口登录页面"""

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
        
        print("检查Login.tsx源码...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 3 'placeholder=' /opt/ai-novel-media-agent/frontend/src/pages/Login.tsx | head -20")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查构建后的文件...")
        stdin, stdout, stderr = ssh.exec_command("ls -lh /var/www/frontend/assets/*.js")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查构建时间...")
        stdin, stdout, stderr = ssh.exec_command("stat /var/www/frontend/index.html | grep Modify")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查JS文件内容...")
        stdin, stdout, stderr = ssh.exec_command("grep -o '请输入用户名\|请输入邮箱' /var/www/frontend/assets/*.js | head -5")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        
        if '请输入用户名' in output:
            print("✓ 找到'请输入用户名'")
        elif '请输入邮箱' in output:
            print("✗ 还是'请输入邮箱'，需要重新构建")
        else:
            print("未找到相关文本")
        
        print("\n测试页面访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:8000/ | grep -o '<title>.*</title>'")
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
