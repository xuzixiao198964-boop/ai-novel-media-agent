#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新配置文件并重启服务"""

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
    password = "8TbXfNYaywmW"

    print(f"连接到服务器 {host}...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, 22, username, password, timeout=30)
        print("SSH连接成功\n")

        # 1. 上传修复后的config.py
        print("上传config.py...")
        sftp = ssh.open_sftp()
        sftp.put("E:/work/ai-novel-media-agent/backend/app/config.py",
                 "/opt/ai-novel-media-agent/backend/app/config.py")
        sftp.close()
        print("上传完成")

        # 2. 重启服务
        run_command(ssh, "systemctl restart ai-novel-media-agent", "重启服务", 10)
        time.sleep(5)

        # 3. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查服务状态", 10)

        # 4. 查看日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 20 --no-pager", "查看日志", 10)

        # 5. 测试API
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

        # 6. 测试外部访问
        print("\n测试外部访问:")
        import requests
        try:
            response = requests.get(f"http://{host}:9000/health", timeout=10)
            print(f"健康检查: {response.status_code} - {response.text}")

            response = requests.post(f"http://{host}:9000/auth/register",
                json={"username":"15606537209","password":"198964","email":"test@example.com"},
                timeout=10)
            print(f"注册: {response.status_code} - {response.text}")

            response = requests.post(f"http://{host}:9000/auth/login",
                json={"username":"15606537209","password":"198964"},
                timeout=10)
            print(f"登录: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"外部访问失败: {e}")

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
