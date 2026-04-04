#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查后端服务状态并修复"""

import paramiko
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(ssh, command, description="", timeout=30):
    """执行SSH命令"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print('='*60)

    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()

        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')

        if output:
            print(output)
        if error and exit_status != 0:
            print(f"错误: {error}")

        return exit_status, output, error
    except Exception as e:
        print(f"命令执行异常: {e}")
        return -1, "", str(e)

def main():
    host = "104.244.90.202"
    username = "root"
    password = "vDyCuc83NxWw"

    print(f"连接到服务器 {host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, 22, username, password, timeout=30, banner_timeout=60)
        print("SSH连接成功\n")

        # 1. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager -l", "检查服务状态", 10)

        # 2. 查看详细日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 50 --no-pager", "查看服务日志", 10)

        # 3. 检查端口
        run_command(ssh, "netstat -tlnp | grep 9000", "检查9000端口", 10)

        # 4. 测试本地连接
        run_command(ssh, "curl -v http://localhost:9000/health", "测试本地9000端口", 10)
        run_command(ssh, "curl -v http://localhost:9000/api/health", "测试本地API", 10)

        # 5. 检查数据库连接
        run_command(ssh,
            "sudo -u postgres psql -c '\\l' | grep ai_novel",
            "检查数据库", 10)

        # 6. 手动启动测试
        print("\n" + "="*60)
        print("尝试手动启动后端")
        print("="*60)

        run_command(ssh, "systemctl stop ai-novel-media-agent", "停止服务", 10)
        time.sleep(2)

        # 测试手动启动
        run_command(ssh,
            "cd /opt/ai-novel-media-agent/backend && timeout 10 python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 || true",
            "手动启动测试", 15)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
