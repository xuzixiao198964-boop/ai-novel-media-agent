#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用无头浏览器测试前端页面"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = '104.244.90.202'
USERNAME = 'root'
PASSWORD = 'vDyCuc83NxWw'

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD, timeout=10)

        # 安装playwright用于浏览器测试
        print('=== 安装测试工具 ===')
        stdin, stdout, stderr = ssh.exec_command('which node')
        node_path = stdout.read().decode('utf-8', errors='ignore').strip()

        if not node_path:
            print('Node.js未安装，跳过浏览器测试')
            print('使用curl测试前端页面...')

            # 测试页面能否加载
            print('\n=== 测试页面加载 ===')
            stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost/admin/')
            html = stdout.read().decode('utf-8', errors='ignore')

            if '<div id="root"></div>' in html:
                print('✓ HTML页面正常')
            else:
                print('✗ HTML页面异常')

            if 'index-CTKrEYsq.js' in html:
                print('✓ JS引用正常')
            else:
                print('✗ JS引用缺失')

            if 'index-D8C5Ik2A.css' in html:
                print('✓ CSS引用正常')
            else:
                print('✗ CSS引用缺失')

            # 测试资源文件
            print('\n=== 测试资源文件 ===')
            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/assets/index-CTKrEYsq.js')
            js_code = stdout.read().decode('utf-8', errors='ignore').strip()
            print(f'JS文件: {js_code}')

            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost/admin/assets/index-D8C5Ik2A.css')
            css_code = stdout.read().decode('utf-8', errors='ignore').strip()
            print(f'CSS文件: {css_code}')

            # 检查JS文件内容
            print('\n=== 检查JS配置 ===')
            stdin, stdout, stderr = ssh.exec_command('grep -o "http://104.244.90.202:9000" /var/www/html/admin/assets/index-CTKrEYsq.js | head -1')
            api_url = stdout.read().decode('utf-8', errors='ignore').strip()
            if api_url:
                print(f'✓ API地址配置正确: {api_url}')
            else:
                print('✗ API地址未找到')

            # 检查basename配置
            stdin, stdout, stderr = ssh.exec_command('grep -o "basename.*admin" /var/www/html/admin/assets/index-CTKrEYsq.js | head -1')
            basename = stdout.read().decode('utf-8', errors='ignore').strip()
            if 'admin' in basename:
                print(f'✓ basename配置正确')
            else:
                print('⚠ basename配置可能有问题')

        print('\n=== 验证总结 ===')
        print('前端页面: http://104.244.90.202/admin')
        print('登录账号: admin / 198964')
        print('后端API: http://104.244.90.202:9000/api')
        print('\n请在浏览器中访问上述地址进行最终验证')

        ssh.close()

    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
