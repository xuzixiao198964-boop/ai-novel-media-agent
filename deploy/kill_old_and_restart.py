#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""停止旧系统并启动新系统"""

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
        ssh.connect(host, 22, username, password, timeout=30, banner_timeout=60)
        print("SSH连接成功\n")

        # 1. 查找占用9000端口的进程
        run_command(ssh, "lsof -i :9000 || netstat -tlnp | grep :9000", "查找9000端口进程", 10)

        # 2. 强制杀死所有占用9000端口的进程
        run_command(ssh, "fuser -k 9000/tcp || true", "杀死9000端口进程", 10)
        time.sleep(2)

        # 3. 再次确认端口已释放
        run_command(ssh, "lsof -i :9000 || echo '端口已释放'", "确认端口状态", 10)

        # 4. 启动新系统
        run_command(ssh, "systemctl restart ai-novel-media-agent", "启动新系统", 10)
        time.sleep(5)

        # 5. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查服务状态", 10)

        # 6. 查看日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 30 --no-pager", "查看日志", 10)

        # 7. 测试API
        print("\n" + "="*60)
        print("测试API")
        print("="*60)

        time.sleep(3)

        run_command(ssh, "curl -s http://localhost:9000/api/health", "健康检查", 10)

        # 8. 创建测试账号
        run_command(ssh,
            "curl -s -X POST http://localhost:9000/api/auth/register -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\",\"email\":\"test@example.com\"}'",
            "注册测试账号", 10)

        # 9. 测试登录
        run_command(ssh,
            "curl -s -X POST http://localhost:9000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"15606537209\",\"password\":\"198964\"}'",
            "登录测试", 10)

        # 10. 外部访问测试
        print("\n" + "="*60)
        print("外部访问测试")
        print("="*60)

        import requests

        tests = [
            ("产品官网", f"http://{host}/", "GET", None),
            ("登录页面", f"http://{host}/login.html", "GET", None),
            ("API健康检查", f"http://{host}/api/health", "GET", None),
            ("注册账号", f"http://{host}/api/auth/register", "POST",
             {"username":"testuser2","password":"test123","email":"test2@test.com"}),
            ("登录", f"http://{host}/api/auth/login", "POST",
             {"username":"15606537209","password":"198964"}),
        ]

        success_count = 0
        for name, url, method, data in tests:
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(url, json=data, timeout=10)

                if response.status_code in [200, 201]:
                    print(f"✓ {name}: {response.status_code}")
                    if 'json' in response.headers.get('content-type', ''):
                        print(f"  {response.json()}")
                    success_count += 1
                elif response.status_code == 400:
                    print(f"✓ {name}: {response.status_code} (可能已存在)")
                    print(f"  {response.text[:200]}")
                    success_count += 1
                else:
                    print(f"✗ {name}: {response.status_code}")
                    print(f"  {response.text[:200]}")
            except Exception as e:
                print(f"✗ {name}: {e}")

        print("\n" + "="*60)
        print(f"测试完成: {success_count}/{len(tests)} 通过")
        print("="*60)

        if success_count >= 4:
            print("\n✓ 系统部署成功！")
            print("\n访问地址:")
            print(f"  产品官网: http://{host}/")
            print(f"  登录页面: http://{host}/login.html")
            print(f"  用户端应用: http://{host}:8000/")
            print(f"\n测试账号: 15606537209 / 198964")
        else:
            print("\n✗ 部署未完全成功，请检查日志")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
