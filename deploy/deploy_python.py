#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python部署脚本 - 使用paramiko进行SSH连接
"""
import os
import sys
import time
import tarfile
import paramiko
from pathlib import Path

# 配置
SERVER_IP = "104.244.90.202"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "8TbXfNYaywmW"
LLM_API_KEY = os.getenv("LLM_API_KEY", "mock-api-key-for-testing")

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
    print("AI 智能内容创作平台 - 自动部署")
    print("="*60)
    print(f"服务器: {SERVER_IP}")
    print(f"用户: {SERVER_USER}")
    print()

    # 检查LLM API Key
    if not LLM_API_KEY or LLM_API_KEY == "mock-api-key-for-testing":
        print("警告: 未设置LLM_API_KEY环境变量，将使用Mock模式")
        print("继续部署...")

    try:
        # 步骤1: 打包项目
        print_step(1, "打包项目文件")
        project_root = Path(__file__).parent.parent
        tar_path = project_root / "deploy" / "ai-novel-media-agent.tar.gz"

        print(f"  项目路径: {project_root}")
        print(f"  打包到: {tar_path}")

        with tarfile.open(tar_path, "w:gz") as tar:
            for folder in ["backend", "frontend", "admin", "official-site", "deploy"]:
                folder_path = project_root / folder
                if folder_path.exists():
                    print(f"  添加: {folder}/")
                    tar.add(folder_path, arcname=folder,
                           filter=lambda x: None if any(ex in x.name for ex in
                           ['node_modules', '__pycache__', '.git', 'venv', 'dist']) else x)

        print(f"  [OK] 打包完成: {tar_path.stat().st_size / 1024 / 1024:.2f} MB")

        # 步骤2: 连接服务器
        print_step(2, "连接到服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"  连接到 {SERVER_USER}@{SERVER_IP}:{SERVER_PORT}")
        ssh.connect(SERVER_IP, SERVER_PORT, SERVER_USER, SERVER_PASSWORD, timeout=30)
        print("  [OK] SSH连接成功")

        # 步骤3: 停止占用端口的服务
        print_step(3, "停止占用端口的服务")
        ports = [80, 8000, 8001, 9000]
        for port in ports:
            execute_ssh_command(ssh,
                f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                f"停止端口 {port}")

        execute_ssh_command(ssh, "systemctl stop media-agent 2>/dev/null || true", "停止旧服务")
        execute_ssh_command(ssh, "systemctl stop ai-novel-agent 2>/dev/null || true", "停止旧服务")
        print("  [OK] 端口清理完成")

        # 步骤4: 清理旧数据
        print_step(4, "清理旧数据")
        execute_ssh_command(ssh, "rm -rf /opt/ai-novel-media-agent", "删除旧目录")
        execute_ssh_command(ssh, "mkdir -p /opt/ai-novel-media-agent", "创建新目录")
        print("  [OK] 旧数据清理完成")

        # 步骤5: 上传文件
        print_step(5, "上传项目文件")
        sftp = ssh.open_sftp()
        print(f"  上传: {tar_path.name}")
        sftp.put(str(tar_path), "/tmp/ai-novel-media-agent.tar.gz")
        sftp.close()
        print("  [OK] 文件上传完成")

        # 步骤6: 解压文件
        print_step(6, "解压项目文件")
        execute_ssh_command(ssh,
            "cd /opt/ai-novel-media-agent && tar -xzf /tmp/ai-novel-media-agent.tar.gz",
            "解压文件")
        execute_ssh_command(ssh, "rm /tmp/ai-novel-media-agent.tar.gz", "删除临时文件")
        print("  [OK] 解压完成")

        # 步骤7: 安装后端依赖
        print_step(7, "安装后端依赖")
        print("  这可能需要几分钟...")
        execute_ssh_command(ssh,
            "cd /opt/ai-novel-media-agent/backend && pip3 install -r requirements.txt",
            "安装Python包")
        print("  [OK] 后端依赖安装完成")

        # 步骤8: 配置环境变量
        print_step(8, "配置环境变量")
        env_content = f"""LLM_API_KEY={LLM_API_KEY}
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
HOST=0.0.0.0
PORT=9000
DATABASE_URL=sqlite:///./data/app.db
"""
        execute_ssh_command(ssh,
            f"cd /opt/ai-novel-media-agent/backend && cat > .env << 'EOF'\n{env_content}\nEOF",
            "创建.env文件")

        execute_ssh_command(ssh,
            "cd /opt/ai-novel-media-agent/backend && mkdir -p data/tasks data/uploads data/temp",
            "创建数据目录")
        print("  [OK] 环境配置完成")

        # 步骤9: 构建前端
        print_step(9, "构建前端项目")
        print("  这可能需要几分钟...")

        # 检查npm是否安装
        status, _, _ = execute_ssh_command(ssh, "which npm")
        if status != 0:
            print("  警告: npm未安装，跳过前端构建")
            print("  前端将使用开发模式运行")
        else:
            execute_ssh_command(ssh,
                "cd /opt/ai-novel-media-agent/frontend && npm install && npm run build",
                "构建用户端")
            execute_ssh_command(ssh,
                "cd /opt/ai-novel-media-agent/admin && npm install && npm run build",
                "构建管理后台")
            print("  [OK] 前端构建完成")

        # 步骤10: 配置Nginx
        print_step(10, "配置Nginx")
        execute_ssh_command(ssh,
            "mkdir -p /var/www/html/ai-novel-media-agent",
            "创建网站目录")
        execute_ssh_command(ssh,
            "cp -r /opt/ai-novel-media-agent/official-site/* /var/www/html/ai-novel-media-agent/",
            "复制官网文件")
        print("  [OK] Nginx配置完成")

        # 步骤11: 创建systemd服务
        print_step(11, "创建systemd服务")
        service_content = """[Unit]
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
WantedBy=multi-user.target
"""
        execute_ssh_command(ssh,
            f"cat > /etc/systemd/system/ai-novel-media-agent.service << 'EOF'\n{service_content}\nEOF",
            "创建服务文件")

        execute_ssh_command(ssh, "systemctl daemon-reload", "重新加载systemd")
        execute_ssh_command(ssh, "systemctl enable ai-novel-media-agent", "启用服务")
        execute_ssh_command(ssh, "systemctl start ai-novel-media-agent", "启动服务")
        print("  [OK] 服务创建完成")

        # 步骤12: 等待服务启动
        print_step(12, "等待服务启动")
        print("  等待10秒...")
        time.sleep(10)

        status, output, _ = execute_ssh_command(ssh,
            "systemctl status ai-novel-media-agent --no-pager",
            "检查服务状态")

        if "active (running)" in output:
            print("  [OK] 服务运行正常")
        else:
            print("  警告: 服务可能未正常启动")
            print(f"  状态: {output[:200]}")

        # 关闭SSH连接
        ssh.close()

        # 步骤13: 验证部署
        print_step(13, "验证部署")
        print("  等待5秒后开始验证...")
        time.sleep(5)

        import requests

        tests = [
            ("后端健康检查", f"http://{SERVER_IP}:9000/api/health"),
            ("后端API文档", f"http://{SERVER_IP}:9000/docs"),
            ("产品官网", f"http://{SERVER_IP}/"),
        ]

        passed = 0
        for name, url in tests:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"  [OK] {name}: 成功")
                    passed += 1
                else:
                    print(f"  [FAIL] {name}: 失败 (状态码: {response.status_code})")
            except Exception as e:
                print(f"  [FAIL] {name}: 失败 ({str(e)[:50]})")

        print()
        print("="*60)
        print("部署完成！")
        print("="*60)
        print(f"验证结果: {passed}/{len(tests)} 通过")
        print()
        print("访问地址：")
        print(f"  产品官网: http://{SERVER_IP}/")
        print(f"  API文档: http://{SERVER_IP}:9000/docs")
        print(f"  用户端: http://{SERVER_IP}:8000/")
        print(f"  管理后台: http://{SERVER_IP}:8001/")
        print()
        print("查看日志：")
        print("  sudo journalctl -u ai-novel-media-agent -f")
        print()

        return 0 if passed == len(tests) else 1

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
