#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整验证用户端前后端功能"""

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
    print("=" * 80)
    print("用户端完整验证")
    print("=" * 80)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 1. 验证前端部署
        print("\n【1】前端部署验证")
        print("-" * 80)
        frontend_check = """
echo "前端文件:"
ls -lh /var/www/ai-novel-media-agent/frontend/index.html
ls /var/www/ai-novel-media-agent/frontend/assets/ | wc -l | xargs echo "资源文件数:"

echo ""
echo "HTTP访问测试:"
curl -s -o /dev/null -w "用户端首页: HTTP %{http_code}\n" http://localhost:8000/
"""
        status, output, error = execute_ssh_command(ssh, frontend_check)
        print(output)

        # 2. 验证后端API - 认证相关
        print("\n【2】后端API验证 - 认证")
        print("-" * 80)
        auth_check = """
echo "健康检查:"
curl -s http://localhost:9000/api/health

echo ""
echo ""
echo "注册接口测试:"
curl -s -X POST http://localhost:9000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser123","email":"test@example.com","password":"test123456","phone":"13800138000"}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print('注册成功，返回token')
    elif 'detail' in data:
        print(f\"注册失败: {data['detail']}\")
    else:
        print('注册接口返回:', data)
except:
    print('注册接口异常')
"

echo ""
echo "登录接口测试:"
curl -s -X POST http://localhost:9000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"198964"}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'access_token' in data:
        print('登录成功')
        print(f\"Token: {data['access_token'][:50]}...\")
    else:
        print('登录失败:', data)
except Exception as e:
    print('登录接口异常:', e)
"
"""
        status, output, error = execute_ssh_command(ssh, auth_check)
        print(output)

        # 3. 验证后端API - 任务相关
        print("\n【3】后端API验证 - 任务")
        print("-" * 80)
        task_check = """
echo "获取任务列表:"
curl -s http://localhost:9000/api/tasks | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(f\"任务列表返回: {len(data)}个任务\")
    elif 'items' in data:
        print(f\"任务列表返回: {len(data['items'])}个任务\")
    else:
        print('任务列表格式:', type(data))
except Exception as e:
    print('任务接口异常:', e)
"
"""
        status, output, error = execute_ssh_command(ssh, task_check)
        print(output)

        # 4. 验证后端API - 内容相关
        print("\n【4】后端API验证 - 内容")
        print("-" * 80)
        content_check = """
echo "小说列表:"
curl -s http://localhost:9000/api/novels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(f\"小说列表: {len(data)}篇\")
    elif 'items' in data:
        print(f\"小说列表: {len(data['items'])}篇\")
    else:
        print('小说接口返回:', type(data))
except Exception as e:
    print('小说接口异常:', e)
"

echo ""
echo "视频列表:"
curl -s http://localhost:9000/api/videos | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        print(f\"视频列表: {len(data)}个\")
    elif 'items' in data:
        print(f\"视频列表: {len(data['items'])}个\")
    else:
        print('视频接口返回:', type(data))
except Exception as e:
    print('视频接口异常:', e)
"
"""
        status, output, error = execute_ssh_command(ssh, content_check)
        print(output)

        # 5. 验证后端API - 用户相关
        print("\n【5】后端API验证 - 用户")
        print("-" * 80)
        user_check = """
echo "用户信息接口:"
curl -s http://localhost:9000/api/users/me 2>&1 | head -5

echo ""
echo "套餐信息接口:"
curl -s http://localhost:9000/api/users/subscription 2>&1 | head -5
"""
        status, output, error = execute_ssh_command(ssh, user_check)
        print(output)

        # 6. 检查前端页面文件
        print("\n【6】前端页面文件检查")
        print("-" * 80)
        pages_check = """
echo "前端页面文件:"
ls /opt/ai-novel-media-agent/frontend/src/pages/*.tsx | while read file; do
    basename $file
done
"""
        status, output, error = execute_ssh_command(ssh, pages_check)
        print(output)

        # 7. 检查前端是否使用真实API
        print("\n【7】前端API配置检查")
        print("-" * 80)
        api_config_check = """
echo "检查API client配置:"
cat /opt/ai-novel-media-agent/frontend/src/api/client.ts | grep -A 5 "baseURL"
"""
        status, output, error = execute_ssh_command(ssh, api_config_check)
        print(output)

        # 8. 运行测试用例
        print("\n【8】运行测试用例")
        print("-" * 80)
        test_check = """
cd /opt/ai-novel-media-agent/backend
echo "运行单元测试:"
python3 -m pytest tests/unit/ -v --tb=short 2>&1 | tail -20

echo ""
echo "运行集成测试:"
python3 -m pytest tests/integration/ -v --tb=short 2>&1 | tail -20
"""
        status, output, error = execute_ssh_command(ssh, test_check)
        print(output)

        ssh.close()

        print("\n" + "=" * 80)
        print("验证总结")
        print("=" * 80)
        print("\n访问地址:")
        print("  用户端: http://104.244.90.202:8000")
        print("  管理端: http://104.244.90.202/admin")
        print("  API文档: http://104.244.90.202:9000/docs")
        print("\n测试账号:")
        print("  管理员: admin / 198964")
        print("\n前端页面:")
        print("  - Dashboard (仪表盘)")
        print("  - CreateTask (创建任务)")
        print("  - Tasks (我的任务)")
        print("  - Novels (小说作品)")
        print("  - Videos (视频作品)")
        print("  - Square (作品广场)")
        print("  - Package (套餐管理)")
        print("  - Recharge (充值)")
        print("  - Billing (消费记录)")
        print("  - Platforms (平台绑定)")
        print("  - Settings (设置)")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
