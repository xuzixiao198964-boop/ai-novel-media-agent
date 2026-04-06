#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在服务器上重新构建并部署前端"""

import paramiko
import sys
import io

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
    print("在服务器上重新构建并部署前端")
    print("=" * 60)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        print("\n[1/3] 构建前端...")
        build_script = """
cd /opt/ai-novel-media-agent/admin
npm run build
"""
        status, output, error = execute_ssh_command(ssh, build_script)
        print(output)
        if error and "error" in error.lower():
            print(f"构建错误: {error}")

        print("\n[2/3] 部署到Nginx目录...")
        deploy_script = """
# 备份旧文件
if [ -d /var/www/ai-novel-media-agent/admin ]; then
    mv /var/www/ai-novel-media-agent/admin /var/www/ai-novel-media-agent/admin.backup.$(date +%Y%m%d_%H%M%S)
fi

# 复制新文件
cp -r /opt/ai-novel-media-agent/admin/dist /var/www/ai-novel-media-agent/admin

echo "部署完成"
ls -la /var/www/ai-novel-media-agent/admin | head -20
"""
        status, output, error = execute_ssh_command(ssh, deploy_script)
        print(output)

        print("\n[3/3] 验证部署...")
        verify_script = """
# 检查文件
echo "=== 检查index.html ==="
ls -lh /var/www/ai-novel-media-agent/admin/index.html

echo ""
echo "=== 检查assets目录 ==="
ls -lh /var/www/ai-novel-media-agent/admin/assets/ | head -10

echo ""
echo "=== 测试访问 ==="
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost/admin/
"""
        status, output, error = execute_ssh_command(ssh, verify_script)
        print(output)

        ssh.close()

        print("\n" + "=" * 60)
        print("部署完成！")
        print("=" * 60)
        print("\n访问地址: http://104.244.90.202/admin")
        print("登录账号: admin / 198964")
        print("\n请登录后点击左侧菜单的 '系统配置' 查看API密钥配置界面")
        print("\nAPI密钥配置包括:")
        print("  1. OpenAI (小说生成) - API Key + Base URL")
        print("  2. 视频生成服务 - API Key + API URL")
        print("  3. 语音合成服务 (TTS) - API Key + API URL")
        print("  4. 图片生成服务 - API Key + API URL")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
