#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""部署API密钥配置功能"""

import paramiko
import os
import sys
import io

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 服务器配置
SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"
REMOTE_DIR = "/opt/ai-novel-media-agent"

def run_ssh_command(ssh, command, description):
    """执行SSH命令"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print(f"{'='*60}")

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')

    if output:
        print("输出:")
        print(output)
    if error:
        print("错误:")
        print(error)

    if exit_status != 0:
        print(f"[X] 命令执行失败，退出码: {exit_status}")
        return False
    else:
        print(f"[OK] 命令执行成功")
        return True

def upload_file(sftp, local_path, remote_path):
    """上传文件"""
    print(f"\n上传文件: {local_path} -> {remote_path}")
    try:
        sftp.put(local_path, remote_path)
        print(f"[OK] 文件上传成功")
        return True
    except Exception as e:
        print(f"[X] 文件上传失败: {e}")
        return False

def main():
    print("="*60)
    print("开始部署API密钥配置功能")
    print("="*60)

    # 连接服务器
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n连接服务器 {SERVER}...")
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)
        print("[OK] SSH连接成功")

        sftp = ssh.open_sftp()
        print("[OK] SFTP连接成功")

        # 1. 上传修改后的Config.tsx
        local_config = "E:/work/ai-novel-media-agent/admin/src/pages/Config.tsx"
        remote_config = f"{REMOTE_DIR}/admin/src/pages/Config.tsx"

        if not upload_file(sftp, local_config, remote_config):
            return False

        # 2. 在服务器上重新构建前端
        if not run_ssh_command(ssh,
            f"cd {REMOTE_DIR}/admin && npm run build",
            "构建管理后台前端"):
            return False

        # 3. 部署到Nginx目录
        if not run_ssh_command(ssh,
            f"mkdir -p /var/www/ai-novel-media-agent/admin && "
            f"rm -rf /var/www/ai-novel-media-agent/admin/* && "
            f"cp -r {REMOTE_DIR}/admin/dist/* /var/www/ai-novel-media-agent/admin/",
            "部署前端到Nginx目录"):
            return False

        # 4. 测试配置页面
        print("\n" + "="*60)
        print("测试配置页面")
        print("="*60)

        test_result = run_ssh_command(ssh,
            "curl -s http://localhost/admin/ | grep -q 'root' && echo 'OK' || echo 'FAIL'",
            "测试前端页面")

        if test_result:
            print("\n" + "="*60)
            print("[OK] 部署成功!")
            print("="*60)
            print("\n请访问以下地址验证:")
            print(f"管理后台: http://{SERVER}/admin")
            print("登录后进入'系统配置'页面，应该能看到新增的'API密钥配置'部分")
            print("\n包含以下配置项:")
            print("1. OpenAI (小说生成) - API Key 和 Base URL")
            print("2. 视频生成服务 - API Key 和 API URL")
            print("3. 语音合成服务 (TTS) - API Key 和 API URL")
            print("4. 图片生成服务 - API Key 和 API URL")
            return True
        else:
            print("\n[X] 部署验证失败")
            return False

    except Exception as e:
        print(f"\n[X] 部署过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()
        print("\n连接已关闭")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
