#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "104.244.90.202"
USER = "root"
PASSWORD = "vDyCuc83NxWw"

def restart_backend():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接到服务器 {HOST}...")
        ssh.connect(HOST, username=USER, password=PASSWORD)

        # 停止旧进程
        print("停止旧进程...")
        stdin, stdout, stderr = ssh.exec_command("pkill -f 'uvicorn app.main:app' || true")
        stdout.read()

        import time
        time.sleep(2)

        # 启动新进程（在backend目录下）
        print("启动后端服务...")
        start_cmd = """cd /opt/ai-novel-media-agent/backend && \
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/backend.log 2>&1 &"""

        stdin, stdout, stderr = ssh.exec_command(start_cmd)
        stdout.read()

        time.sleep(3)

        # 检查服务状态
        print("\n检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep uvicorn | grep -v grep")
        ps_result = stdout.read().decode()

        if ps_result:
            print("✓ 后端服务运行中")
            print(ps_result)
        else:
            print("✗ 后端服务未运行")
            print("\n查看错误日志:")
            stdin, stdout, stderr = ssh.exec_command("tail -50 /var/log/backend.log")
            log = stdout.read().decode()
            print(log)
            return

        # 测试健康检查
        print("\n测试健康检查...")
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:9000/api/health")
        health = stdout.read().decode()
        print(f"健康检查: {health}")

        print("\n✓ 后端服务启动成功！")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    restart_backend()
