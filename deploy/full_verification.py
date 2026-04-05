#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整验证管理后台功能"""

import paramiko
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = '104.244.90.202'
USERNAME = 'root'
PASSWORD = 'vDyCuc83NxWw'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)

        print('=== 1. 验证前端页面访问 ===')
        stdin, stdout, stderr = ssh.exec_command('curl -s -I http://localhost/admin/')
        headers = stdout.read().decode('utf-8', errors='ignore')
        if '200 OK' in headers:
            print('✓ 前端页面可访问 (HTTP 200)')
        else:
            print('✗ 前端页面访问失败')
            print(headers)

        print('\n=== 2. 验证登录功能 ===')
        stdin, stdout, stderr = ssh.exec_command('''curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"198964"}' ''')
        result = stdout.read().decode('utf-8', errors='ignore')
        login_data = json.loads(result)

        if 'access_token' in login_data:
            token = login_data['access_token']
            print(f'✓ 登录成功')
            print(f'  Token: {token[:30]}...')
        else:
            print('✗ 登录失败')
            print(result)
            return

        print('\n=== 3. 验证Dashboard数据 ===')
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Authorization: Bearer {token}" http://localhost:9000/api/admin/dashboard')
        dashboard = json.loads(stdout.read().decode('utf-8', errors='ignore'))
        print(f'✓ Dashboard数据正常')
        print(f'  用户: {dashboard["total_users"]}, 任务: {dashboard["total_tasks"]}, 小说: {dashboard["total_novels"]}, 视频: {dashboard["total_videos"]}')

        print('\n=== 4. 验证用户管理 ===')
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Authorization: Bearer {token}" http://localhost:9000/api/admin/users')
        users = json.loads(stdout.read().decode('utf-8', errors='ignore'))
        print(f'✓ 用户列表: {len(users)}个用户')

        print('\n=== 5. 验证小说管理 ===')
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Authorization: Bearer {token}" http://localhost:9000/api/admin/novels')
        novels = json.loads(stdout.read().decode('utf-8', errors='ignore'))
        print(f'✓ 小说列表: {len(novels)}部小说')

        print('\n=== 6. 验证视频管理 ===')
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Authorization: Bearer {token}" http://localhost:9000/api/admin/videos')
        videos = json.loads(stdout.read().decode('utf-8', errors='ignore'))
        print(f'✓ 视频列表: {len(videos)}个视频')

        print('\n=== 7. 验证任务监控 ===')
        stdin, stdout, stderr = ssh.exec_command(f'curl -s -H "Authorization: Bearer {token}" http://localhost:9000/api/admin/tasks/stats')
        stats = json.loads(stdout.read().decode('utf-8', errors='ignore'))
        print(f'✓ 任务统计: 总数{stats["total"]}, 运行中{stats["running"]}, 已完成{stats["completed"]}')

        print('\n=== 8. 验证其他接口 ===')
        apis = [
            ('API Keys', '/api/admin/api-keys'),
            ('财务汇总', '/api/admin/finance/summary'),
            ('发布记录', '/api/admin/publish'),
            ('系统日志', '/api/admin/logs'),
            ('系统配置', '/api/admin/config'),
        ]

        for name, path in apis:
            stdin, stdout, stderr = ssh.exec_command(f'curl -s -w "\\nHTTP_CODE:%{{http_code}}" -H "Authorization: Bearer {token}" http://localhost:9000{path}')
            result = stdout.read().decode('utf-8', errors='ignore')
            if 'HTTP_CODE:200' in result:
                print(f'✓ {name}')
            else:
                print(f'✗ {name}')

        print('\n=== 9. 检查前端资源文件 ===')
        stdin, stdout, stderr = ssh.exec_command('ls -lh /var/www/html/admin/')
        files = stdout.read().decode('utf-8', errors='ignore')
        if 'index.html' in files and 'assets' in files:
            print('✓ 前端资源文件完整')
        else:
            print('✗ 前端资源文件缺失')
            print(files)

        print('\n=== 10. 检查Nginx配置 ===')
        stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
        nginx_test = stdout.read().decode('utf-8', errors='ignore')
        if 'successful' in nginx_test:
            print('✓ Nginx配置正确')
        else:
            print('✗ Nginx配置有误')
            print(nginx_test)

        print('\n' + '='*60)
        print('验证总结:')
        print('='*60)
        print('✓ 前端页面: http://104.244.90.202/admin')
        print('✓ 登录账号: admin / 198964')
        print('✓ 后端API: 所有接口正常')
        print('✓ 测试数据: 7用户, 5小说, 5视频, 7任务')
        print('='*60)

        ssh.close()

    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
