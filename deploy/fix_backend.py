#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复后端服务"""

import paramiko
import time
import sys
import io

# 设置stdout为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_ssh_command(ssh, command, description=""):
    """执行SSH命令"""
    if description:
        print(f"\n{'='*60}")
        print(f"{description}")
        print(f"命令: {command}")
        print('='*60)

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    if output:
        print(output)
    if error and exit_status != 0:
        print(f"错误: {error}", file=sys.stderr)

    return exit_status, output, error

def main():
    host = "104.244.90.202"
    port = 22
    username = "root"
    password = "8TbXfNYaywmW"

    print(f"连接到服务器 {host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=30)
        print("SSH连接成功\n")

        # 1. 停止旧系统
        run_ssh_command(ssh, "pkill -f 'python.*9000'", "停止占用9000端口的旧系统")
        time.sleep(2)

        # 2. 进入项目目录并安装依赖
        run_ssh_command(ssh,
            "cd /opt/ai-novel-media-agent/backend && pip3 install -r requirements.txt",
            "安装Python依赖")

        # 3. 创建数据库目录
        run_ssh_command(ssh, "mkdir -p /opt/ai-novel-media-agent/backend/data", "创建数据库目录")

        # 4. 重启服务
        run_ssh_command(ssh, "systemctl restart ai-novel-media-agent", "重启后端服务")
        time.sleep(5)

        # 5. 检查服务状态
        run_ssh_command(ssh, "systemctl status ai-novel-media-agent", "检查服务状态")

        # 6. 查看日志
        run_ssh_command(ssh, "journalctl -u ai-novel-media-agent -n 30 --no-pager", "查看服务日志")

        # 7. 测试API
        print("\n" + "="*60)
        print("测试API")
        print("="*60)

        run_ssh_command(ssh, "curl -s http://localhost:9000/health", "测试健康检查")

        run_ssh_command(ssh,
            """curl -s -X POST http://localhost:9000/auth/register \
            -H "Content-Type: application/json" \
            -d '{"username":"15606537209","password":"198964","email":"test@example.com"}'""",
            "测试注册API")

        run_ssh_command(ssh,
            """curl -s -X POST http://localhost:9000/auth/login \
            -H "Content-Type: application/json" \
            -d '{"username":"15606537209","password":"198964"}'""",
            "测试登录API")

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
