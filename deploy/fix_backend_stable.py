#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""稳定版后端修复脚本"""

import paramiko
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(ssh, command, description="", timeout=30):
    """执行SSH命令，带超时控制"""
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
    password = "8TbXfNYaywmW"

    print(f"连接到服务器 {host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, 22, username, password, timeout=30)
        print("SSH连接成功\n")

        # 1. 停止旧系统
        run_command(ssh, "pkill -f 'python.*9000' || true", "停止旧系统", 10)
        time.sleep(2)

        # 2. 检查项目目录
        run_command(ssh, "ls -la /opt/ai-novel-media-agent/backend/", "检查项目目录", 10)

        # 3. 安装依赖（分批安装，避免超时）
        print("\n安装核心依赖...")
        deps = [
            "fastapi uvicorn[standard]",
            "sqlalchemy pydantic",
            "python-jose[cryptography] passlib[bcrypt]",
            "python-multipart aiofiles",
            "httpx requests",
            "celery redis",
            "openai anthropic"
        ]

        for dep in deps:
            status, _, _ = run_command(ssh,
                f"cd /opt/ai-novel-media-agent/backend && pip3 install {dep} --quiet",
                f"安装 {dep}", 60)
            if status != 0:
                print(f"警告: {dep} 安装可能失败")

        # 4. 创建必要目录
        run_command(ssh, "mkdir -p /opt/ai-novel-media-agent/backend/data", "创建数据目录", 10)

        # 5. 重启服务
        run_command(ssh, "systemctl stop ai-novel-media-agent", "停止服务", 10)
        time.sleep(2)
        run_command(ssh, "systemctl start ai-novel-media-agent", "启动服务", 10)
        time.sleep(5)

        # 6. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查服务状态", 10)

        # 7. 查看日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 20 --no-pager", "查看日志", 10)

        # 8. 测试API
        print("\n" + "="*60)
        print("测试API")
        print("="*60)

        run_command(ssh, "curl -s http://localhost:9000/health", "健康检查", 10)

        run_command(ssh,
            "curl -s -X POST http://localhost:9000/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\",\"email\":\"test@example.com\"}'",
            "注册测试账号", 10)

        run_command(ssh,
            "curl -s -X POST http://localhost:9000/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\"}'",
            "登录测试", 10)

        print("\n" + "="*60)
        print("修复完成")
        print("="*60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
