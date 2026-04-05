#!/usr/bin/env python3
"""最终验证管理后台"""

import paramiko
import sys

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def main():
    print("=" * 60)
    print("最终验证管理后台")
    print("=" * 60)

    try:
        # 连接服务器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)

        # 测试所有登录方式
        print("\n[1/4] 测试登录")
        test_users = [
            ('admin', '198964'),
            ('15606537209', '198964'),
        ]

        tokens = {}
        for username, password in test_users:
            cmd = f'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{{"username":"{username}","password":"{password}"}}\''
            stdout, stderr = run_command(ssh, cmd)
            if '"access_token"' in stdout:
                print(f"  [OK] {username} 登录成功")
                import json
                try:
                    data = json.loads(stdout)
                    tokens[username] = data['access_token']
                except:
                    pass
            else:
                print(f"  [FAIL] {username} 登录失败")

        # 测试API访问
        if tokens:
            print("\n[2/4] 测试API访问")
            token = list(tokens.values())[0]

            # 测试获取用户信息
            cmd = f'curl -s -H "Authorization: Bearer {token}" http://localhost:9000/api/users/me'
            stdout, stderr = run_command(ssh, cmd)
            if '"username"' in stdout:
                print("  [OK] 获取用户信息成功")
            else:
                print(f"  [FAIL] 获取用户信息失败: {stdout[:100]}")

        # 测试前端访问
        print("\n[3/4] 测试前端访问")
        endpoints = [
            ('管理后台首页', 'http://localhost/admin'),
            ('管理后台index.html', 'http://localhost/admin/index.html'),
            ('API文档', 'http://localhost:9000/docs'),
            ('健康检查', 'http://localhost:9000/api/health'),
        ]

        for name, url in endpoints:
            cmd = f'curl -s -o /dev/null -w "%{{http_code}}" {url}'
            stdout, stderr = run_command(ssh, cmd)
            status_code = stdout.strip()
            if status_code in ['200', '304']:
                print(f"  [OK] {name}: {status_code}")
            else:
                print(f"  [WARN] {name}: {status_code}")

        # 检查服务状态
        print("\n[4/4] 检查服务状态")
        services = [
            ('后端服务', 'systemctl is-active ai-novel-media-agent'),
            ('Nginx', 'systemctl is-active nginx'),
        ]

        for name, cmd in services:
            stdout, stderr = run_command(ssh, cmd)
            status = stdout.strip()
            if status == 'active':
                print(f"  [OK] {name}: {status}")
            else:
                print(f"  [WARN] {name}: {status}")

        ssh.close()

        print("\n" + "=" * 60)
        print("验证完成")
        print("=" * 60)
        print("\n部署信息:")
        print("  管理后台: http://104.244.90.202/admin")
        print("  API文档: http://104.244.90.202:9000/docs")
        print("  健康检查: http://104.244.90.202:9000/api/health")
        print("\n登录凭据:")
        print("  用户名: admin 或 15606537209")
        print("  密码: 198964")
        print("\n请在浏览器中访问管理后台进行测试！")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
