#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新构建并部署前端"""

import paramiko
import sys
import io
import os
import subprocess

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

def main():
    print("=" * 60)
    print("重新构建并部署前端")
    print("=" * 60)

    # 本地构建
    print("\n[1/4] 本地构建前端...")
    os.chdir(r"E:\work\ai-novel-media-agent\admin")

    result = subprocess.run(["npm", "run", "build"], shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"构建失败: {result.stderr}")
        return
    print("构建成功")

    # 打包
    print("\n[2/4] 打包构建文件...")
    os.chdir(r"E:\work\ai-novel-media-agent")
    result = subprocess.run(["tar", "-czf", "admin-dist.tar.gz", "-C", "admin/dist", "."],
                          shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"打包失败: {result.stderr}")
        return
    print("打包成功")

    # 上传到服务器
    print("\n[3/4] 上传到服务器...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        sftp = ssh.open_sftp()
        sftp.put(r"E:\work\ai-novel-media-agent\admin-dist.tar.gz",
                "/tmp/admin-dist.tar.gz")
        sftp.close()
        print("上传成功")

        # 部署
        print("\n[4/4] 部署到服务器...")
        deploy_script = """
# 备份旧文件
if [ -d /var/www/ai-novel-media-agent/admin ]; then
    mv /var/www/ai-novel-media-agent/admin /var/www/ai-novel-media-agent/admin.backup.$(date +%Y%m%d_%H%M%S)
fi

# 创建目录
mkdir -p /var/www/ai-novel-media-agent/admin

# 解压
cd /var/www/ai-novel-media-agent/admin
tar -xzf /tmp/admin-dist.tar.gz

# 清理
rm /tmp/admin-dist.tar.gz

echo "部署完成"
ls -la /var/www/ai-novel-media-agent/admin
"""
        status, output, error = execute_ssh_command(ssh, deploy_script)
        print(output)
        if error:
            print(f"错误: {error}")

        ssh.close()

        print("\n" + "=" * 60)
        print("部署完成！")
        print("=" * 60)
        print("\n访问地址: http://104.244.90.202/admin")
        print("登录账号: admin / 198964")
        print("\n请访问 系统配置 页面查看API密钥配置界面")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
