#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
import sys
import time
import io

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("连接服务器...")
        ssh.connect('104.244.90.202', username='root', password='vDyCuc83NxWw', timeout=10)

        print("\n=== 重新构建管理后台 ===")
        commands = [
            'cd /opt/ai-novel-media-agent/admin',
            'export NODE_OPTIONS=--max-old-space-size=2048',
            'npm run build'
        ]

        stdin, stdout, stderr = ssh.exec_command(' && '.join(commands), get_pty=True)

        # 等待完成并获取输出
        output = stdout.read().decode('utf-8', errors='ignore')
        # 只打印关键信息
        for line in output.split('\n'):
            if 'error' in line.lower() or 'built in' in line.lower() or 'build' in line.lower():
                print(line)

        # 等待命令完成
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("\n=== 部署到Nginx ===")
            stdin, stdout, stderr = ssh.exec_command('rm -rf /var/www/html/admin/* && cp -r /opt/ai-novel-media-agent/admin/dist/* /var/www/html/admin/')
            stdout.channel.recv_exit_status()
            print("部署完成")

            print("\n=== 验证部署 ===")
            stdin, stdout, stderr = ssh.exec_command('head -20 /var/www/html/admin/index.html')
            print(stdout.read().decode('utf-8', errors='ignore'))

            print("\n=== 测试访问 ===")
            stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost/admin/ | head -20')
            print(stdout.read().decode('utf-8', errors='ignore'))
        else:
            print(f"\n构建失败，退出码: {exit_status}")
            sys.exit(1)

        ssh.close()
        print("\n完成！请访问: http://104.244.90.202/admin")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
