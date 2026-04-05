#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动部署和测试脚本
服务器: 104.244.90.202
"""

import paramiko
import os
import sys
import time
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 服务器配置
SERVER_IP = "104.244.90.202"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "vDyCuc83NxWw"

# 本地文件路径
LOCAL_PACKAGE = Path(__file__).parent.parent / "full-deploy.tar.gz"

def print_step(step_num, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step_num}: {message}")
    print('='*60)

def execute_remote_command(ssh, command, print_output=True):
    """执行远程命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if print_output:
        if output:
            print(output)
        if error:
            print(f"错误: {error}", file=sys.stderr)

    return exit_status, output, error

def main():
    print("="*60)
    print("AI智能内容创作平台 - 自动部署和测试")
    print("="*60)

    # 检查本地文件
    if not LOCAL_PACKAGE.exists():
        print(f"错误: 找不到部署包 {LOCAL_PACKAGE}")
        print("请先运行打包命令生成 full-deploy.tar.gz")
        return 1

    try:
        # 连接SSH
        print_step(1, "连接到服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_IP, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print(f"[OK] 已连接到 {SERVER_IP}")

        # 上传文件
        print_step(2, "上传部署包")
        sftp = ssh.open_sftp()
        remote_path = "/tmp/full-deploy.tar.gz"
        sftp.put(str(LOCAL_PACKAGE), remote_path)
        sftp.close()
        print(f"[OK] 已上传到 {remote_path}")

        # 解压项目
        print_step(3, "解压项目")
        commands = [
            "cd /opt",
            "rm -rf ai-novel-media-agent",
            "mkdir -p ai-novel-media-agent",
            "cd ai-novel-media-agent",
            "tar -xzf /tmp/full-deploy.tar.gz"
        ]
        execute_remote_command(ssh, " && ".join(commands))
        print("[OK] 项目已解压")

        # 安装后端依赖
        print_step(4, "安装后端依赖")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && pip3 install -r requirements.txt")
        print("[OK] 后端依赖已安装")

        # 配置环境变量
        print_step(5, "配置环境变量")
        env_content = """LLM_API_KEY=sk-9fcc8f6d0ce94fdbbe66b152b7d3e485
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
HOST=0.0.0.0
PORT=9000
DATABASE_URL=sqlite:///./data/app.db
REDIS_URL=redis://localhost:6379/0"""

        execute_remote_command(ssh, f"cd /opt/ai-novel-media-agent/backend && cat > .env << 'EOF'\n{env_content}\nEOF")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && mkdir -p data/tasks data/uploads data/temp")
        print("[OK] 环境变量已配置")

        # 构建管理端
        print_step(6, "构建管理端")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/admin && npm install")
        execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/admin && npm run build")
        print("[OK] 管理端已构建")

        # 部署官网
        print_step(7, "部署官网")
        execute_remote_command(ssh, "mkdir -p /var/www/html/ai-novel-media-agent")
        execute_remote_command(ssh, "cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/ai-novel-media-agent/")
        print("[OK] 官网已部署")

        # 配置Nginx
        print_step(8, "配置Nginx")
        nginx_config = """server {
    listen 80;
    server_name _;

    # 产品官网
    location / {
        root /var/www/html/ai-novel-media-agent;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 管理后台
    location /admin {
        alias /opt/ai-novel-media-agent/admin/dist;
        index index.html;
        try_files $uri $uri/ /admin/index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}"""

        execute_remote_command(ssh, f"cat > /etc/nginx/sites-available/ai-novel-media-agent << 'EOF'\n{nginx_config}\nEOF")
        execute_remote_command(ssh, "ln -sf /etc/nginx/sites-available/ai-novel-media-agent /etc/nginx/sites-enabled/")
        execute_remote_command(ssh, "nginx -t && systemctl reload nginx")
        print("[OK] Nginx已配置")

        # 配置后端服务
        print_step(9, "配置后端服务")
        service_config = """[Unit]
Description=AI Novel Media Agent Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ai-novel-media-agent/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=3
Environment="PYTHONPATH=/opt/ai-novel-media-agent/backend"

[Install]
WantedBy=multi-user.target"""

        execute_remote_command(ssh, f"cat > /etc/systemd/system/ai-novel-media-agent.service << 'EOF'\n{service_config}\nEOF")
        execute_remote_command(ssh, "systemctl daemon-reload")
        execute_remote_command(ssh, "systemctl enable ai-novel-media-agent")
        execute_remote_command(ssh, "systemctl restart ai-novel-media-agent")
        print("[OK] 后端服务已启动")

        # 等待服务启动
        print("\n等待服务启动...")
        time.sleep(10)

        # 验证部署
        print_step(10, "验证部署")
        status, output, error = execute_remote_command(ssh, "systemctl status ai-novel-media-agent --no-pager", print_output=False)
        if "active (running)" in output:
            print("[OK] 后端服务运行正常")
        else:
            print("[FAIL] 后端服务未正常运行")
            print(output)

        # 运行单元测试
        print_step(11, "运行单元测试")
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && pytest tests/unit/ -v --tb=short")

        if status == 0:
            print("[OK] 单元测试全部通过")
        else:
            print("[FAIL] 单元测试失败")
            print("需要查看详细错误并修复")

        # 运行集成测试
        print_step(12, "运行集成测试")
        status, output, error = execute_remote_command(ssh, "cd /opt/ai-novel-media-agent/backend && pytest tests/integration/ -v --tb=short")

        if status == 0:
            print("[OK] 集成测试全部通过")
        else:
            print("[FAIL] 集成测试失败")
            print("需要查看详细错误并修复")

        # 总结
        print("\n" + "="*60)
        print("部署和测试完成！")
        print("="*60)
        print("\n访问地址：")
        print(f"  产品官网: http://{SERVER_IP}/")
        print(f"  管理后台: http://{SERVER_IP}/admin")
        print(f"  API文档: http://{SERVER_IP}:9000/docs")
        print("\n查看日志：")
        print("  ssh root@104.244.90.202")
        print("  journalctl -u ai-novel-media-agent -f")

        ssh.close()
        return 0

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
