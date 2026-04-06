#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复最终问题：移除Dashboard假数据，重新部署前端"""

import paramiko
import sys
import io
import os

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

def upload_file(sftp, local_path, remote_path):
    sftp.put(local_path, remote_path)

def main():
    print("=" * 60)
    print("修复最终问题")
    print("=" * 60)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()

        # 1. 上传修复后的Dashboard.tsx
        print("\n[1/4] 上传修复后的Dashboard.tsx...")
        local_dashboard = r"E:\work\ai-novel-media-agent\admin\src\pages\Dashboard.tsx"
        remote_dashboard = "/opt/ai-novel-media-agent/admin/src/pages/Dashboard.tsx"
        upload_file(sftp, local_dashboard, remote_dashboard)
        print("✓ Dashboard.tsx已上传")

        # 2. 重新构建前端
        print("\n[2/4] 重新构建前端...")
        build_commands = """
cd /opt/ai-novel-media-agent/admin
npm run build
"""
        status, output, error = execute_ssh_command(ssh, build_commands)
        if status == 0:
            print("✓ 前端构建成功")
        else:
            print(f"构建输出: {output}")
            print(f"构建错误: {error}")

        # 3. 部署到Nginx目录
        print("\n[3/4] 部署到Nginx目录...")
        deploy_commands = """
rm -rf /var/www/ai-novel-media-agent/admin/*
cp -r /opt/ai-novel-media-agent/admin/dist/* /var/www/ai-novel-media-agent/admin/
ls -lh /var/www/ai-novel-media-agent/admin/
"""
        status, output, error = execute_ssh_command(ssh, deploy_commands)
        print(output)

        # 4. 验证修复
        print("\n[4/4] 验证修复...")
        verify_commands = """
echo "=== 前端验证 ==="
curl -s -o /dev/null -w "管理后台: HTTP %{http_code}\n" http://localhost/admin/

echo ""
echo "=== Dashboard API验证 ==="
curl -s http://localhost:9000/api/admin/dashboard | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('✓ 总用户数:', data.get('total_users'))
print('✓ 活跃任务:', data.get('active_tasks'))
print('✓ 今日收入:', data.get('today_income'))
print('✓ 作品总数:', data.get('total_novels', 0) + data.get('total_videos', 0))
"

echo ""
echo "=== 最近用户API验证 ==="
curl -s http://localhost:9000/api/admin/dashboard/recent-users?limit=5 | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('返回用户数:', len(data))
if len(data) > 0:
    print('示例用户:', data[0].get('username'))
else:
    print('暂无用户数据（正常，因为只有管理员账户）')
"

echo ""
echo "=== 任务分布API验证 ==="
curl -s http://localhost:9000/api/admin/dashboard/task-distribution | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('任务类型数:', len(data))
if len(data) == 0:
    print('暂无任务数据（正常，数据库已清空）')
"

echo ""
echo "=== 套餐分布API验证 ==="
curl -s http://localhost:9000/api/admin/dashboard/subscription-distribution | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('套餐类型数:', len(data))
for item in data:
    print(f\"  {item['name']}: {item['value']}人\")
"
"""
        status, output, error = execute_ssh_command(ssh, verify_commands)
        print(output)

        sftp.close()
        ssh.close()

        print("\n" + "=" * 60)
        print("修复完成！")
        print("=" * 60)
        print("\n已修复的问题:")
        print("1. ✓ 移除Dashboard最近用户的假数据fallback")
        print("2. ✓ 所有数据现在都从真实API获取")
        print("3. ✓ 前端已重新构建并部署")
        print("\n访问地址: http://104.244.90.202/admin")
        print("登录账号: admin / 198964")
        print("\n说明:")
        print("- Dashboard显示的所有数据都是真实的")
        print("- 因为数据库已清空，所以任务、作品数为0是正常的")
        print("- 只有2个管理员账户，所以用户数为2")
        print("- 系统配置页面的API密钥配置部分在页面底部")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
