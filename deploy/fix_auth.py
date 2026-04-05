#!/usr/bin/env python3
"""修改auth.py使用SHA256验证"""

import paramiko
import sys

SERVER = "104.244.90.202"
PORT = 22
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"

def run_command(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def main():
    print("=" * 60)
    print("修改auth.py密码验证方式")
    print("=" * 60)

    try:
        # 连接服务器
        print("\n[1/3] 连接服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("[OK] 已连接")

        # 停止服务
        print("\n[2/3] 停止服务")
        run_command(ssh, "systemctl stop ai-novel-media-agent")
        print("[OK] 已停止")

        # 备份并修改auth.py
        print("\n[3/3] 修改auth.py")
        modify_script = """
cd /opt/ai-novel-media-agent/backend/app/api
cp auth.py auth.py.bak

# 读取当前文件
python3 << 'PYEOF'
import re

with open('auth.py', 'r') as f:
    content = f.read()

# 找到verify_password函数并替换
old_func = r'def verify_password\\(plain_password: str, hashed_password: str\\) -> bool:[^}]+?return bcrypt\\.checkpw\\([^)]+\\)'

new_func = '''def verify_password(plain_password: str, hashed_password: str) -> bool:
    import hashlib
    sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    if sha256_hash == hashed_password:
        return True
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False'''

content = re.sub(old_func, new_func, content, flags=re.DOTALL)

with open('auth.py', 'w') as f:
    f.write(content)

print("auth.py已修改")
PYEOF
"""
        stdout, stderr = run_command(ssh, modify_script)
        print(stdout)
        if stderr and "error" in stderr.lower():
            print(f"[ERROR] {stderr}")

        # 启动服务
        print("\n[4/3] 启动服务")
        run_command(ssh, "systemctl start ai-novel-media-agent")
        import time
        time.sleep(3)
        stdout, stderr = run_command(ssh, "systemctl status ai-novel-media-agent")
        if "active (running)" in stdout:
            print("[OK] 服务已启动")
        else:
            print("[WARNING] 服务状态异常")

        # 测试登录
        print("\n[5/3] 测试登录")
        test_commands = [
            ('admin', 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\''),
            ('15606537209', 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"15606537209","password":"198964"}\''),
        ]

        for name, cmd in test_commands:
            stdout, stderr = run_command(ssh, cmd)
            if '"access_token"' in stdout:
                print(f"[OK] {name} 登录成功")
            else:
                print(f"[FAIL] {name} 登录失败: {stdout[:200]}")

        ssh.close()

        print("\n" + "=" * 60)
        print("修改完成")
        print("=" * 60)
        print("\n登录信息:")
        print("  用户名: admin 或 15606537209")
        print("  密码: 198964")
        print("  URL: http://104.244.90.202/admin")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
