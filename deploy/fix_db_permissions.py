#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复数据库权限"""

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

        # 1. 修复数据库权限
        run_command(ssh,
            """sudo -u postgres psql -d ai_novel_media -c "GRANT ALL ON SCHEMA public TO ai_novel;" """,
            "授予schema权限", 10)

        run_command(ssh,
            """sudo -u postgres psql -d ai_novel_media -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ai_novel;" """,
            "授予表权限", 10)

        run_command(ssh,
            """sudo -u postgres psql -d ai_novel_media -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ai_novel;" """,
            "授予序列权限", 10)

        run_command(ssh,
            """sudo -u postgres psql -d ai_novel_media -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ai_novel;" """,
            "设置默认表权限", 10)

        run_command(ssh,
            """sudo -u postgres psql -d ai_novel_media -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ai_novel;" """,
            "设置默认序列权限", 10)

        # 2. 重启后端服务
        run_command(ssh, "systemctl restart ai-novel-media-agent", "重启后端服务", 10)

        print("\n等待服务启动...")
        time.sleep(8)

        # 3. 检查服务状态
        run_command(ssh, "systemctl status ai-novel-media-agent --no-pager", "检查服务状态", 10)

        # 4. 查看日志
        run_command(ssh, "journalctl -u ai-novel-media-agent -n 20 --no-pager", "查看服务日志", 10)

        # 5. 检查端口
        run_command(ssh, "netstat -tlnp | grep 9000", "检查9000端口", 10)

        # 6. 测试API
        print("\n" + "="*60)
        print("测试API")
        print("="*60)

        run_command(ssh, "curl -s http://localhost:9000/api/health", "健康检查", 10)

        # 7. 注册测试账号
        run_command(ssh,
            """curl -s -X POST http://localhost:9000/api/auth/register -H 'Content-Type: application/json' -d '{"username":"15606537209","password":"198964","email":"test@example.com"}'""",
            "注册测试账号", 10)

        # 8. 测试登录
        run_command(ssh,
            """curl -s -X POST http://localhost:9000/api/auth/login -H 'Content-Type: application/json' -d '{"username":"15606537209","password":"198964"}'""",
            "登录测试", 10)

        # 9. 外部访问测试
        print("\n" + "="*60)
        print("外部访问测试")
        print("="*60)

        import requests

        tests = [
            ("产品官网", f"http://{host}/", "GET", None),
            ("登录页面", f"http://{host}/login.html", "GET", None),
            ("API健康检查", f"http://{host}/api/health", "GET", None),
            ("注册账号", f"http://{host}/api/auth/register", "POST",
             {"username":"testuser","password":"test123","email":"test@test.com"}),
            ("登录", f"http://{host}/api/auth/login", "POST",
             {"username":"15606537209","password":"198964"}),
            ("用户端应用", f"http://{host}:8000/", "GET", None),
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
                        result = response.json()
                        if 'access_token' in result:
                            print(f"  登录成功！Token: {result['access_token'][:30]}...")
                        else:
                            print(f"  {result}")
                    success_count += 1
                elif response.status_code == 400:
                    print(f"✓ {name}: {response.status_code} (可能已存在)")
                    print(f"  {response.text[:150]}")
                    success_count += 1
                else:
                    print(f"✗ {name}: {response.status_code}")
                    print(f"  {response.text[:200]}")
            except Exception as e:
                print(f"✗ {name}: {e}")

        print("\n" + "="*60)
        print(f"测试完成: {success_count}/{len(tests)} 通过")
        print("="*60)

        if success_count >= 5:
            print("\n" + "="*60)
            print("✓✓✓ 部署成功！✓✓✓")
            print("="*60)
            print(f"\n访问地址:")
            print(f"  产品官网: http://{host}/")
            print(f"  登录页面: http://{host}/login.html")
            print(f"  用户端应用: http://{host}:8000/")
            print(f"  API文档: http://{host}/docs")
            print(f"\n测试账号: 15606537209 / 198964")
        else:
            print("\n✗ 还有问题需要解决")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
