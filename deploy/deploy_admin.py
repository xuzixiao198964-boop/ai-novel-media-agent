#!/usr/bin/env python3
"""部署管理后台到服务器"""
import paramiko
import os
from pathlib import Path

# 服务器配置
SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"
PORT = 22

def deploy_admin():
    """部署管理后台"""
    print("开始部署管理后台...")

    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接服务器 {SERVER}...")
        ssh.connect(SERVER, port=PORT, username=USERNAME, password=PASSWORD)

        sftp = ssh.open_sftp()

        # 本地路径
        local_admin_dir = Path("E:/work/ai-novel-media-agent/admin/dist")

        # 服务器路径
        remote_admin_dir = "/var/www/html/admin"

        # 创建远程目录
        print(f"创建远程目录 {remote_admin_dir}...")
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_admin_dir}")
        stdout.channel.recv_exit_status()

        # 上传管理后台文件
        print("上传管理后台文件...")

        def upload_dir(local_dir, remote_dir):
            """递归上传目录"""
            for item in local_dir.iterdir():
                local_path = item
                remote_path = f"{remote_dir}/{item.name}"

                if item.is_file():
                    print(f"  上传: {item.name}")
                    sftp.put(str(local_path), remote_path)
                elif item.is_dir():
                    # 创建远程目录
                    try:
                        sftp.mkdir(remote_path)
                    except:
                        pass
                    upload_dir(local_path, remote_path)

        upload_dir(local_admin_dir, remote_admin_dir)

        # 设置权限
        print("设置文件权限...")
        stdin, stdout, stderr = ssh.exec_command(f"chmod -R 755 {remote_admin_dir}")
        stdout.channel.recv_exit_status()

        # 重启 Nginx
        print("重启 Nginx...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart nginx")
        stdout.channel.recv_exit_status()

        print("\n[OK] 管理后台部署成功！")
        print(f"访问地址: http://{SERVER}:8001/")

        sftp.close()

    except Exception as e:
        print(f"[ERROR] 部署失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_admin()
