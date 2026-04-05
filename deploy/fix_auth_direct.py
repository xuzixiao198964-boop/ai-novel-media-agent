#!/usr/bin/env python3
"""直接替换auth.py中的verify_password函数"""

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
    print("直接替换verify_password函数")
    print("=" * 60)

    try:
        # 连接服务器
        print("\n[1/4] 连接服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("[OK] 已连接")

        # 停止服务
        print("\n[2/4] 停止服务")
        run_command(ssh, "systemctl stop ai-novel-media-agent")
        print("[OK] 已停止")

        # 直接替换函数
        print("\n[3/4] 替换verify_password函数")
        replace_script = """
cd /opt/ai-novel-media-agent/backend/app/api
cp auth.py auth.py.bak2

cat auth.py | python3 -c "
import sys
content = sys.stdin.read()

# 找到函数定义的位置
lines = content.split('\\n')
new_lines = []
skip = False
for i, line in enumerate(lines):
    if 'def verify_password' in line:
        # 替换整个函数
        new_lines.append('def verify_password(plain_password, hashed_password):')
        new_lines.append('    import hashlib')
        new_lines.append('    sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()')
        new_lines.append('    if sha256_hash == hashed_password:')
        new_lines.append('        return True')
        new_lines.append('    try:')
        new_lines.append('        return bcrypt.checkpw(plain_password.encode(\"utf-8\"), hashed_password.encode(\"utf-8\"))')
        new_lines.append('    except:')
        new_lines.append('        return False')
        skip = True
    elif skip and line.startswith('def '):
        # 遇到下一个函数定义，停止跳过
        skip = False
        new_lines.append(line)
    elif not skip:
        new_lines.append(line)

print('\\n'.join(new_lines))
" > auth.py.new

mv auth.py.new auth.py
echo "替换完成"
"""
        stdout, stderr = run_command(ssh, replace_script)
        print(stdout)
        if stderr and "error" in stderr.lower():
            print(f"[ERROR] {stderr}")

        # 验证修改
        print("\n[3.5/4] 验证修改")
        stdout, stderr = run_command(ssh, "grep -A 10 'def verify_password' /opt/ai-novel-media-agent/backend/app/api/auth.py")
        print(stdout)

        # 启动服务
        print("\n[4/4] 启动服务")
        run_command(ssh, "systemctl start ai-novel-media-agent")
        import time
        time.sleep(3)
        stdout, stderr = run_command(ssh, "systemctl status ai-novel-media-agent")
        if "active (running)" in stdout:
            print("[OK] 服务已启动")
        else:
            print("[WARNING] 服务状态异常")
            print(stdout[-500:])

        # 测试登录
        print("\n[5/4] 测试登录")
        test_commands = [
            ('admin', 'curl -s -X POST http://localhost:9000/api/auth/login -H "Content-Type: application/json" -d \'{"username":"admin","password":"198964"}\''),
        ]

        for name, cmd in test_commands:
            stdout, stderr = run_command(ssh, cmd)
            if '"access_token"' in stdout:
                print(f"[OK] {name} 登录成功！")
                print(f"Token: {stdout[:100]}...")
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
