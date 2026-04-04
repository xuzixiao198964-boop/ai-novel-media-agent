#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复部署脚本 - 修复官网和前端问题
"""
import os
import sys
import paramiko

# 配置
SERVER_IP = "104.244.90.202"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "8TbXfNYaywmW"

def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step}: {message}")
    print('='*60)

def execute_ssh_command(ssh, command, description=""):
    """执行SSH命令"""
    if description:
        print(f"  执行: {description}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if exit_status != 0 and error:
        print(f"  警告: {error[:200]}")

    return exit_status, output, error

def main():
    print("="*60)
    print("修复部署 - 官网和前端")
    print("="*60)

    try:
        # 连接服务器
        print_step(1, "连接到服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, SERVER_PORT, SERVER_USER, SERVER_PASSWORD, timeout=30)
        print("  [OK] SSH连接成功")

        # 修复官网
        print_step(2, "修复产品官网")

        # 清理旧的官网文件
        execute_ssh_command(ssh,
            "rm -rf /var/www/html/*",
            "清理旧的官网文件")

        # 复制新的官网文件
        execute_ssh_command(ssh,
            "cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/",
            "复制新的官网文件")

        # 设置权限
        execute_ssh_command(ssh,
            "chmod -R 755 /var/www/html/",
            "设置文件权限")

        print("  [OK] 官网文件已更新")

        # 检查npm是否可用
        print_step(3, "检查前端构建环境")
        status, output, _ = execute_ssh_command(ssh, "which npm")

        if status == 0:
            print("  [OK] npm已安装，开始构建前端")

            # 构建用户端
            print_step(4, "构建用户端Web应用")
            print("  这可能需要几分钟...")
            execute_ssh_command(ssh,
                "cd /opt/ai-novel-media-agent/frontend && npm install --legacy-peer-deps && npm run build",
                "构建用户端")
            print("  [OK] 用户端构建完成")

            # 构建管理后台
            print_step(5, "构建管理后台")
            print("  这可能需要几分钟...")
            execute_ssh_command(ssh,
                "cd /opt/ai-novel-media-agent/admin && npm install --legacy-peer-deps && npm run build",
                "构建管理后台")
            print("  [OK] 管理后台构建完成")

            # 配置Nginx服务前端
            print_step(6, "配置Nginx服务前端")

            nginx_config = """server {
    listen 80;
    server_name _;

    # 产品官网
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 用户端 Web
    location /app {
        alias /opt/ai-novel-media-agent/frontend/dist;
        try_files $uri $uri/ /app/index.html;
    }

    # 管理后台
    location /admin {
        alias /opt/ai-novel-media-agent/admin/dist;
        try_files $uri $uri/ /admin/index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}"""

            execute_ssh_command(ssh,
                f"cat > /etc/nginx/sites-available/default << 'EOF'\n{nginx_config}\nEOF",
                "更新Nginx配置")

            execute_ssh_command(ssh, "nginx -t", "测试Nginx配置")
            execute_ssh_command(ssh, "systemctl reload nginx", "重新加载Nginx")

            print("  [OK] Nginx配置已更新")

        else:
            print("  [警告] npm未安装，跳过前端构建")
            print("  前端应用需要手动构建")

        # 验证部署
        print_step(7, "验证部署")

        import requests
        import time

        time.sleep(3)

        tests = [
            ("产品官网", f"http://{SERVER_IP}/"),
            ("后端API", f"http://{SERVER_IP}:9000/api/health"),
        ]

        passed = 0
        for name, url in tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # 检查官网内容
                    if "官网" in name:
                        if "AI 创作平台" in response.text or "AI创作平台" in response.text:
                            print(f"  [OK] {name}: 成功（内容正确）")
                            passed += 1
                        else:
                            print(f"  [警告] {name}: 可访问但内容可能不对")
                    else:
                        print(f"  [OK] {name}: 成功")
                        passed += 1
                else:
                    print(f"  [FAIL] {name}: 失败 (状态码: {response.status_code})")
            except Exception as e:
                print(f"  [FAIL] {name}: 失败 ({str(e)[:50]})")

        ssh.close()

        print()
        print("="*60)
        print("修复完成！")
        print("="*60)
        print(f"验证结果: {passed}/{len(tests)} 通过")
        print()
        print("访问地址：")
        print(f"  产品官网: http://{SERVER_IP}/")
        print(f"  用户端: http://{SERVER_IP}/app")
        print(f"  管理后台: http://{SERVER_IP}/admin")
        print(f"  API文档: http://{SERVER_IP}:9000/docs")
        print()

        return 0 if passed == len(tests) else 1

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
