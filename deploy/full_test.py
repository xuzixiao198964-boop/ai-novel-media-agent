#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理旧进程并全面测试前端"""

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

        # 1. 查找并停止所有占用9000端口的进程
        run_command(ssh, "lsof -ti:9000 | xargs kill -9 || true", "停止所有9000端口进程", 10)
        time.sleep(2)

        # 2. 重启服务
        run_command(ssh, "systemctl restart ai-novel-media-agent", "重启服务", 10)
        time.sleep(5)

        # 3. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查服务状态", 10)

        # 4. 查看日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 20 --no-pager", "查看日志", 10)

        # 5. 测试API
        print("\n" + "="*60)
        print("测试后端API")
        print("="*60)

        run_command(ssh, "curl -s http://localhost:9000/health", "健康检查", 10)
        run_command(ssh, "curl -s http://localhost:9000/", "根路径", 10)

        # 6. 创建测试账号
        run_command(ssh,
            "curl -s -X POST http://localhost:9000/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\",\"email\":\"test@example.com\"}'",
            "注册测试账号", 10)

        # 7. 测试登录
        run_command(ssh,
            "curl -s -X POST http://localhost:9000/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\"}'",
            "登录测试", 10)

        # 8. 测试外部访问
        print("\n" + "="*60)
        print("测试外部访问")
        print("="*60)

        import requests

        # 健康检查
        try:
            response = requests.get(f"http://{host}:9000/health", timeout=10)
            print(f"✓ 健康检查: {response.status_code}")
            print(f"  响应: {response.text}")
        except Exception as e:
            print(f"✗ 健康检查失败: {e}")

        # 注册
        try:
            response = requests.post(f"http://{host}:9000/auth/register",
                json={"username":"15606537209","password":"198964","email":"test@example.com"},
                timeout=10)
            print(f"\n✓ 注册: {response.status_code}")
            print(f"  响应: {response.text}")
        except Exception as e:
            print(f"\n✗ 注册失败: {e}")

        # 登录
        try:
            response = requests.post(f"http://{host}:9000/auth/login",
                json={"username":"15606537209","password":"198964"},
                timeout=10)
            print(f"\n✓ 登录: {response.status_code}")
            print(f"  响应: {response.text}")
        except Exception as e:
            print(f"\n✗ 登录失败: {e}")

        # 9. 测试前端页面
        print("\n" + "="*60)
        print("测试前端页面")
        print("="*60)

        pages = [
            ("产品官网", f"http://{host}/"),
            ("登录页面", f"http://{host}/login.html"),
            ("用户端应用", f"http://{host}:8000/"),
            ("管理后台", f"http://{host}:8001/"),
            ("API文档", f"http://{host}:9000/docs"),
        ]

        for name, url in pages:
            try:
                response = requests.get(url, timeout=10)
                status = "✓" if response.status_code == 200 else "✗"
                print(f"{status} {name}: {response.status_code} - {url}")
            except Exception as e:
                print(f"✗ {name}: 失败 - {e}")

        print("\n" + "="*60)
        print("测试完成")
        print("="*60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
