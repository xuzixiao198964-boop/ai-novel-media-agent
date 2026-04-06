#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""上传frontend项目到服务器"""

import paramiko
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def execute_ssh_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return exit_status, output, error

def upload_directory(sftp, local_dir, remote_dir):
    """递归上传目录"""
    try:
        sftp.stat(remote_dir)
    except:
        sftp.mkdir(remote_dir)

    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + '/' + item

        if os.path.isfile(local_path):
            print(f"  上传: {item}")
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            # 跳过node_modules和dist
            if item in ['node_modules', 'dist', '.git']:
                continue
            print(f"  创建目录: {item}")
            upload_directory(sftp, local_path, remote_path)

def main():
    print("=" * 70)
    print("上传frontend项目到服务器")
    print("=" * 70)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()

        # 1. 创建目录
        print("\n[1/3] 创建远程目录...")
        create_dir = """
mkdir -p /opt/ai-novel-media-agent/frontend
"""
        status, output, error = execute_ssh_command(ssh, create_dir)
        print("目录已创建")

        # 2. 上传frontend项目
        print("\n[2/3] 上传frontend项目...")
        local_frontend = r"E:\work\ai-novel-media-agent\frontend"
        remote_frontend = "/opt/ai-novel-media-agent/frontend"

        print("上传文件中...")
        upload_directory(sftp, local_frontend, remote_frontend)
        print("上传完成")

        # 3. 验证上传
        print("\n[3/3] 验证上传...")
        verify_cmd = """
echo "检查frontend目录:"
ls -la /opt/ai-novel-media-agent/frontend/

echo ""
echo "检查package.json:"
cat /opt/ai-novel-media-agent/frontend/package.json

echo ""
echo "检查页面文件:"
ls /opt/ai-novel-media-agent/frontend/src/pages/*.tsx | wc -l | xargs echo "页面数:"
"""
        status, output, error = execute_ssh_command(ssh, verify_cmd)
        print(output)

        sftp.close()
        ssh.close()

        print("\n" + "=" * 70)
        print("上传完成")
        print("=" * 70)
        print("\n下一步: 运行 deploy_frontend_8000.py 进行构建和部署")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
