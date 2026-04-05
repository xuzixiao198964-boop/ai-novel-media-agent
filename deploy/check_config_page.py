#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查配置页面"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

    # 检查部署的Config.tsx文件内容
    stdin, stdout, stderr = ssh.exec_command("cat /var/www/ai-novel-media-agent/admin/index.html")
    html = stdout.read().decode('utf-8')
    print("HTML文件内容:")
    print(html)
    print("\n" + "="*60)

    # 检查JS文件是否包含API密钥相关代码
    stdin, stdout, stderr = ssh.exec_command("grep -r 'API密钥配置' /var/www/ai-novel-media-agent/admin/assets/ || echo 'NOT FOUND'")
    result = stdout.read().decode('utf-8')
    print("搜索'API密钥配置':")
    print(result)
    print("\n" + "="*60)

    # 检查源文件
    stdin, stdout, stderr = ssh.exec_command("tail -100 /opt/ai-novel-media-agent/admin/src/pages/Config.tsx")
    config_tsx = stdout.read().decode('utf-8')
    print("Config.tsx 最后100行:")
    print(config_tsx)

finally:
    ssh.close()
