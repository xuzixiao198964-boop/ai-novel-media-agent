#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速部署更新
"""
import paramiko
import os
import tarfile
import sys

SERVER_IP = "104.244.90.202"
SERVER_USER = "root"
SERVER_PASSWORD = "8TbXfNYaywmW"

def exec_cmd(ssh, cmd, desc=""):
    if desc:
        print(f"  {desc}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')

def main():
    print("快速部署更新")
    print("="*60)

    os.chdir("E:/work/ai-novel-media-agent")

    # 打包
    print("\n[1/4] 打包文件")
    tar_path = "update.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add("frontend/dist", arcname="frontend/dist")
        tar.add("admin/dist", arcname="admin/dist")
        tar.add("official-site", arcname="official-site")
    print(f"  打包完成: {os.path.getsize(tar_path)} bytes")

    # 上传
    print("\n[2/4] 上传到服务器")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, 22, SERVER_USER, SERVER_PASSWORD, timeout=30)

    sftp = ssh.open_sftp()
    remote_tar = f"/tmp/{tar_path}"
    sftp.put(tar_path, remote_tar)
    sftp.close()
    print(f"  上传完成")

    # 解压
    print("\n[3/4] 解压并部署")
    exec_cmd(ssh, f"cd /opt/ai-novel-media-agent && tar -xzf {remote_tar}", "解压")
    exec_cmd(ssh, "cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/", "更新官网")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/frontend/dist", "设置权限")
    exec_cmd(ssh, "chmod -R 755 /opt/ai-novel-media-agent/admin/dist", "设置权限")
    exec_cmd(ssh, "chmod -R 755 /var/www/html", "设置权限")
    print("  部署完成")

    # 重载Nginx
    print("\n[4/4] 重载Nginx")
    exec_cmd(ssh, "systemctl reload nginx", "重载")
    print("  Nginx已重载")

    ssh.close()

    print("\n" + "="*60)
    print("部署完成！")
    print("\n访问地址:")
    print("  产品官网: http://104.244.90.202/")
    print("  用户端: http://104.244.90.202:8000/")
    print("  管理后台: http://104.244.90.202:8001/")
    print("  API文档: http://104.244.90.202:9000/docs")

    return 0

if __name__ == "__main__":
    sys.exit(main())
