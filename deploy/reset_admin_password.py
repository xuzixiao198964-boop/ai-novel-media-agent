#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重置admin密码"""

import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        
        print("重置admin密码为198964...")
        
        reset_script = """
import sqlite3
import bcrypt

conn = sqlite3.connect('/opt/ai-novel-media-agent/backend/data/app.db')
cursor = conn.cursor()

# 生成新密码哈希
hashed = bcrypt.hashpw('198964'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 更新admin密码
cursor.execute("UPDATE users SET hashed_password = ? WHERE username = 'admin'", (hashed,))
conn.commit()

# 验证
cursor.execute("SELECT username, email FROM users WHERE username = 'admin'")
user = cursor.fetchone()
print(f"✓ admin密码已重置")
print(f"  用户名: {user[0]}")
print(f"  邮箱: {user[1]}")
print(f"  密码: 198964")

conn.close()
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/tmp/reset_password.py', 'w') as f:
            f.write(reset_script)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command("cd /opt/ai-novel-media-agent/backend && python3 /tmp/reset_password.py")
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 测试登录
        print("\n测试登录...")
        stdin, stdout, stderr = ssh.exec_command("""
            curl -s -X POST http://localhost:9000/api/auth/login \
                -H "Content-Type: application/json" \
                -d '{"username":"admin","password":"198964"}'
        """)
        stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        
        if "access_token" in output:
            print("✓ 登录成功")
        else:
            print("✗ 登录失败")
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    finally:
        ssh.close()

if __name__ == "__main__":
    sys.exit(main())
