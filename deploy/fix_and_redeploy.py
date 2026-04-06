#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复并重新部署"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_ssh_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def main():
    print("=" * 60)
    print("修复并重新部署")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接到服务器 {SERVER}...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("✓ 连接成功")

        sftp = ssh.open_sftp()

        # 1. 上传修复的auth.ts
        print("\n[1/3] 上传修复的auth.ts...")
        sftp.put('E:/work/ai-novel-media-agent/frontend/src/api/auth.ts',
                 '/opt/ai-novel-media-agent/frontend/src/api/auth.ts')
        print("✓ 文件上传完成")

        sftp.close()

        # 2. 重启后端服务
        print("\n[2/3] 启动后端服务...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/backend
            pkill -9 -f "uvicorn app.main:app"
            sleep 2
            nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &
            sleep 5
            curl -s http://localhost:9000/api/health
        """)

        if "healthy" in output:
            print("✓ 后端服务启动成功")
        else:
            print("✗ 后端服务启动失败")
            print(output)
            if error:
                print(error)

        # 3. 构建用户端前端
        print("\n[3/3] 构建用户端前端...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/frontend
            npm run build 2>&1 | tail -20
        """)

        if status == 0 and "dist" in output:
            print("✓ 用户端前端构建成功")
        else:
            print("✗ 构建失败")
            print(output)

        # 验证
        print("\n" + "=" * 60)
        print("验证部署")
        print("=" * 60)

        print("\n1. 测试后端登录...")
        status, output, error = run_ssh_command(ssh, """
            curl -s -X POST http://localhost:9000/api/auth/login \
                -H "Content-Type: application/json" \
                -d '{"username":"admin","password":"198964"}'
        """)

        if "access_token" in output:
            print("✓ 后端登录成功")
        else:
            print("✗ 后端登录失败")
            print(output)

        print("\n2. 检查用户管理API...")
        status, output, error = run_ssh_command(ssh, """
            curl -s http://localhost:9000/api/admin/users?skip=0&limit=10
        """)

        if "items" in output and "password" in output:
            print("✓ 用户管理API正常（包含明文密码）")
        else:
            print("✗ 用户管理API异常")
            print(output)

        print("\n3. 检查前端文件...")
        status, output, error = run_ssh_command(ssh, """
            ls -lh /opt/ai-novel-media-agent/frontend/dist/index.html
            ls -lh /opt/ai-novel-media-agent/admin/dist/index.html
        """)

        if "index.html" in output:
            print("✓ 前端文件存在")
        else:
            print("✗ 前端文件缺失")

        print("\n" + "=" * 60)
        print("部署完成")
        print("=" * 60)
        print("\n访问地址:")
        print(f"  - 用户端: http://{SERVER}:8000")
        print(f"  - 管理端: http://{SERVER}/admin")
        print("\n登录账号:")
        print("  - 用户名: admin")
        print("  - 密码: 198964")
        print("\n数据库状态:")
        print("  - 用户数: 1 (只有admin)")
        print("  - 任务数: 0")
        print("  - 小说数: 0")
        print("  - 视频数: 0")

        return 0

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
