#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复并部署配置保存功能"""

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
    print("修复配置保存功能并部署")
    print("=" * 60)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 上传修复后的文件
        print("\n[1/4] 上传修复后的admin_simple.py...")
        sftp = ssh.open_sftp()
        sftp.put(r"E:\work\ai-novel-media-agent\backend\app\api\admin_simple.py",
                "/opt/ai-novel-media-agent/backend/app/api/admin_simple.py")
        sftp.close()
        print("上传成功")

        # 重启后端服务
        print("\n[2/4] 重启后端服务...")
        restart_script = """
# 查找并停止旧进程
PID=$(ps aux | grep '[u]vicorn app.main:app' | awk '{print $2}')
if [ ! -z "$PID" ]; then
    kill $PID
    sleep 2
    echo "已停止旧进程: $PID"
fi

# 启动新进程
cd /opt/ai-novel-media-agent/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 9000 > /var/log/ai-novel-backend.log 2>&1 &
sleep 3

# 检查进程
NEW_PID=$(ps aux | grep '[u]vicorn app.main:app' | awk '{print $2}')
if [ ! -z "$NEW_PID" ]; then
    echo "后端服务已启动: PID=$NEW_PID"
else
    echo "后端服务启动失败"
    exit 1
fi
"""
        status, output, error = execute_ssh_command(ssh, restart_script)
        print(output)
        if error:
            print(f"错误: {error}")

        # 测试API接口
        print("\n[3/4] 测试API接口...")
        test_script = """
echo "=== 测试GET /api/admin/config ==="
curl -s http://localhost:9000/api/admin/config | python3 -m json.tool | head -30

echo ""
echo "=== 测试PUT /api/admin/config ==="
curl -s -X PUT http://localhost:9000/api/admin/config \
  -H "Content-Type: application/json" \
  -d '{"key":"test_config","value":{"test":"value"},"description":"测试配置"}' \
  | python3 -m json.tool

echo ""
echo "=== 测试Dashboard数据 ==="
curl -s http://localhost:9000/api/admin/dashboard | python3 -m json.tool
"""
        status, output, error = execute_ssh_command(ssh, test_script)
        print(output)

        # 前端验证
        print("\n[4/4] 前端验证...")
        verify_script = """
echo "=== 测试前端访问 ==="
curl -s -o /dev/null -w "管理后台: HTTP %{http_code}\n" http://localhost/admin/

echo ""
echo "=== 检查API代理 ==="
curl -s -o /dev/null -w "API健康检查: HTTP %{http_code}\n" http://localhost:9000/api/health
"""
        status, output, error = execute_ssh_command(ssh, verify_script)
        print(output)

        ssh.close()

        print("\n" + "=" * 60)
        print("部署完成！")
        print("=" * 60)
        print("\n请访问 http://104.244.90.202/admin 验证:")
        print("1. 登录后进入 '系统配置' 页面")
        print("2. 在 'API密钥配置' 部分填写API密钥")
        print("3. 点击 '保存API密钥' 按钮")
        print("4. 应该显示 'API密钥已保存' 提示")
        print("5. 刷新页面，配置应该被保存")
        print("\nDashboard数据说明:")
        print("- 因为数据库已清空，作品总数和活跃任务显示为0是正常的")
        print("- 这些是从真实数据库查询的结果，不是假数据")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
