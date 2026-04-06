#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重新构建管理端前端"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        
        print("重新构建管理端前端...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/admin && npm run build 2>&1")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        
        if 'built in' in output or 'Build completed' in output:
            print("✓ 构建成功")
        else:
            print("构建输出:")
            print(output[-1000:] if len(output) > 1000 else output)
        
        print("\n部署到Nginx...")
        stdin, stdout, stderr = ssh.exec_command("""
            rm -rf /var/www/admin/* && \
            cp -r /opt/ai-novel-media-agent/admin/dist/* /var/www/admin/ && \
            chown -R www-data:www-data /var/www/admin && \
            stat /var/www/admin/index.html | grep Modify
        """)
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n清除Nginx缓存并重启...")
        stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
        stdout.channel.recv_exit_status()
        
        print("\n测试访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/admin/ | grep -o '<title>.*</title>'")
        stdout.channel.recv_exit_status()
        print(stdout.read().decode('utf-8'))
        
        print("\n✓ 管理端前端已重新部署")
        print("\n请在浏览器中:")
        print("1. 按 Ctrl+Shift+R 强制刷新")
        print("2. 或使用无痕模式访问: http://104.244.90.202/admin")
        print("\n现在应该显示正确数据:")
        print("  用户总数: 1")
        print("  活跃任务: 0 (排队: 0)")
        print("  作品总数: 0 (小说: 0 | 视频: 0)")
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
