#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查启动错误"""

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
        
        print("检查启动日志...")
        stdin, stdout, stderr = ssh.exec_command("cat /tmp/backend.log")
        stdout.channel.recv_exit_status()
        log = stdout.read().decode('utf-8')
        print(log if log else "日志为空")
        
        print("\n尝试手动启动并查看错误...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 2>&1 | head -50 &")
        
        import time
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command("cat /tmp/backend.log 2>/dev/null || echo '无日志'")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n检查进程...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print(output if output else "没有进程")
        
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
