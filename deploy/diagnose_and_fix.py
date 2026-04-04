#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断并修复后端API问题"""

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
        print(f"执行: {description}")
        print(f"命令: {command}")
        print('='*60)

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    if output:
        print(output)
    if error:
        print(f"错误: {error}", file=sys.stderr)

    return exit_status, output, error

def main():
    # 服务器配置
    host = "104.244.90.202"
    port = 22
    username = "root"
    password = "8TbXfNYaywmW"

    print(f"连接到服务器 {host}...")

    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=30)
        print("✓ SSH连接成功\n")

        # 1. 检查后端服务状态
        run_ssh_command(ssh, "systemctl status ai-novel-media-agent", "检查后端服务状态")

        # 2. 检查后端日志
        run_ssh_command(ssh, "journalctl -u ai-novel-media-agent -n 50 --no-pager", "查看后端日志")

        # 3. 测试本地API
        run_ssh_command(ssh, "curl -s http://localhost:9000/api/health", "测试健康检查")

        # 4. 测试注册API
        run_ssh_command(ssh,
            """curl -s -X POST http://localhost:9000/api/auth/register \
            -H "Content-Type: application/json" \
            -d '{"username":"15606537209","password":"198964","email":"test@example.com"}'""",
            "测试注册API")

        # 5. 测试登录API
        run_ssh_command(ssh,
            """curl -s -X POST http://localhost:9000/api/auth/login \
            -H "Content-Type: application/json" \
            -d '{"username":"15606537209","password":"198964"}'""",
            "测试登录API")

        # 6. 检查Nginx配置
        run_ssh_command(ssh, "nginx -t", "检查Nginx配置")

        # 7. 查看Nginx日志
        run_ssh_command(ssh, "tail -n 20 /var/log/nginx/error.log", "查看Nginx错误日志")

        # 8. 检查端口监听
        run_ssh_command(ssh, "netstat -tlnp | grep -E ':(80|8000|8001|9000)'", "检查端口监听")

        # 9. 如果服务未运行，尝试重启
        status, output, _ = run_ssh_command(ssh, "systemctl is-active ai-novel-media-agent", "检查服务是否运行")

        if "inactive" in output or "failed" in output:
            print("\n⚠ 后端服务未运行，尝试重启...")
            run_ssh_command(ssh, "systemctl restart ai-novel-media-agent", "重启后端服务")
            time.sleep(3)
            run_ssh_command(ssh, "systemctl status ai-novel-media-agent", "检查重启后状态")

        # 10. 再次测试API
        print("\n" + "="*60)
        print("最终验证")
        print("="*60)

        run_ssh_command(ssh, "curl -s http://localhost:9000/api/health", "健康检查")

        # 11. 测试外部访问
        print("\n测试外部访问:")
        import requests
        try:
            response = requests.get(f"http://{host}:9000/api/health", timeout=10)
            print(f"✓ 外部访问成功: {response.status_code}")
            print(f"  响应: {response.text}")
        except Exception as e:
            print(f"✗ 外部访问失败: {e}")

        print("\n" + "="*60)
        print("诊断完成")
        print("="*60)

    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
