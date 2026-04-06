#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署所有修改到服务器"""

import paramiko
import sys
import io

# 设置标准输出为UTF-8
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
    print("部署所有修改到服务器")
    print("=" * 60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接到服务器 {SERVER}...")
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("✓ 连接成功")

        sftp = ssh.open_sftp()

        # 1. 上传后端修改的文件
        print("\n[1/4] 上传后端文件...")
        files_to_upload = [
            ('E:/work/ai-novel-media-agent/backend/app/api/admin_simple.py',
             '/opt/ai-novel-media-agent/backend/app/api/admin_simple.py'),
        ]

        for local_path, remote_path in files_to_upload:
            print(f"  上传 {local_path.split('/')[-1]}...")
            sftp.put(local_path.replace('\\', '/'), remote_path)
        print("✓ 后端文件上传完成")

        # 2. 上传前端文件
        print("\n[2/4] 上传前端文件...")
        frontend_files = [
            ('E:/work/ai-novel-media-agent/frontend/src/pages/Login.tsx',
             '/opt/ai-novel-media-agent/frontend/src/pages/Login.tsx'),
            ('E:/work/ai-novel-media-agent/frontend/src/store/authStore.ts',
             '/opt/ai-novel-media-agent/frontend/src/store/authStore.ts'),
            ('E:/work/ai-novel-media-agent/frontend/src/api/auth.ts',
             '/opt/ai-novel-media-agent/frontend/src/api/auth.ts'),
        ]

        for local_path, remote_path in frontend_files:
            print(f"  上传 {local_path.split('/')[-1]}...")
            sftp.put(local_path.replace('\\', '/'), remote_path)
        print("✓ 前端文件上传完成")

        # 3. 上传管理端文件
        print("\n[3/4] 上传管理端文件...")
        admin_files = [
            ('E:/work/ai-novel-media-agent/admin/src/pages/Users.tsx',
             '/opt/ai-novel-media-agent/admin/src/pages/Users.tsx'),
            ('E:/work/ai-novel-media-agent/admin/src/pages/Config.tsx',
             '/opt/ai-novel-media-agent/admin/src/pages/Config.tsx'),
        ]

        for local_path, remote_path in admin_files:
            print(f"  上传 {local_path.split('/')[-1]}...")
            sftp.put(local_path.replace('\\', '/'), remote_path)
        print("✓ 管理端文件上传完成")

        sftp.close()

        # 4. 重启后端服务
        print("\n[4/4] 重启后端服务...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/backend
            pkill -f "uvicorn app.main:app"
            sleep 2
            nohup uvicorn app.main:app --host 0.0.0.0 --port 9000 > /tmp/backend.log 2>&1 &
            sleep 3
            curl -s http://localhost:9000/api/health
        """)

        if "healthy" in output:
            print("✓ 后端服务重启成功")
        else:
            print(f"警告: 后端服务可能未正常启动")
            if output:
                print(f"输出: {output}")
            if error:
                print(f"错误: {error}")

        # 5. 构建并部署用户端前端
        print("\n[5/6] 构建用户端前端...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/frontend
            npm run build
        """)

        if status == 0:
            print("✓ 用户端前端构建成功")
        else:
            print(f"✗ 构建失败")
            if error:
                print(error)

        # 6. 构建并部署管理端前端
        print("\n[6/6] 构建管理端前端...")
        status, output, error = run_ssh_command(ssh, """
            cd /opt/ai-novel-media-agent/admin
            npm run build
        """)

        if status == 0:
            print("✓ 管理端前端构建成功")
        else:
            print(f"✗ 构建失败")
            if error:
                print(error)

        # 验证部署
        print("\n" + "=" * 60)
        print("验证部署")
        print("=" * 60)

        print("\n检查后端API...")
        status, output, error = run_ssh_command(ssh, """
            curl -s http://localhost:9000/api/health
            echo ""
            curl -s -X POST http://localhost:9000/api/auth/login \
                -H "Content-Type: application/json" \
                -d '{"username":"admin","password":"198964"}'
        """)

        if "healthy" in output and "access_token" in output:
            print("✓ 后端API正常")
            print("  - 健康检查: 通过")
            print("  - 登录接口: 通过")
        else:
            print("✗ 后端API异常")
            print(output)

        print("\n检查前端部署...")
        status, output, error = run_ssh_command(ssh, """
            ls -lh /opt/ai-novel-media-agent/frontend/dist/index.html
            ls -lh /opt/ai-novel-media-agent/admin/dist/index.html
        """)

        if "index.html" in output:
            print("✓ 前端文件部署成功")
        else:
            print("✗ 前端文件未找到")

        print("\n" + "=" * 60)
        print("部署完成")
        print("=" * 60)
        print("\n访问地址:")
        print(f"  - 用户端: http://{SERVER}:8000")
        print(f"  - 管理端: http://{SERVER}/admin")
        print(f"  - API文档: http://{SERVER}:9000/docs")
        print("\n登录账号:")
        print("  - 用户名: admin")
        print("  - 密码: 198964")

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
