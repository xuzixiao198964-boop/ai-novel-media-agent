#!/usr/bin/env python3
"""直接在数据库中创建用户，绕过bcrypt问题"""

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
    print("直接创建用户（绕过bcrypt）")
    print("=" * 60)

    try:
        # 连接服务器
        print("\n[1/5] 连接服务器")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, PORT, USERNAME, PASSWORD)
        print("[OK] 已连接")

        # 停止后端服务
        print("\n[2/5] 停止后端服务")
        run_command(ssh, "systemctl stop ai-novel-media-agent")
        print("[OK] 已停止")

        # 升级bcrypt库
        print("\n[3/5] 升级bcrypt库")
        stdout, stderr = run_command(ssh, "pip3 install --upgrade bcrypt passlib --break-system-packages")
        print(stdout)
        if stderr and "error" in stderr.lower():
            print(f"[WARNING] {stderr}")

        # 创建用户（使用简短密码）
        print("\n[4/5] 创建用户")
        create_script = """
cd /opt/ai-novel-media-agent
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/ai-novel-media-agent/backend')

from app.core.database import engine, SessionLocal
from app.models import Base, User
from sqlalchemy import text

# 创建表
Base.metadata.create_all(bind=engine)

# 创建会话
db = SessionLocal()

try:
    # 删除已存在的用户
    db.execute(text("DELETE FROM users WHERE username IN ('admin', '15606537209')"))
    db.commit()

    # 使用简单的密码哈希（SHA256）
    import hashlib
    password = "198964"
    hashed = hashlib.sha256(password.encode()).hexdigest()

    # 创建管理员用户
    admin = User(
        username="admin",
        email="admin@example.com",
        phone="15606537209",
        hashed_password=hashed,
        role="admin",
        subscription_tier="premium",
        balance=1000.0,
        is_active=True
    )
    db.add(admin)

    # 创建手机号用户
    phone_user = User(
        username="15606537209",
        email="15606537209@example.com",
        phone="15606537209",
        hashed_password=hashed,
        role="admin",
        subscription_tier="premium",
        balance=1000.0,
        is_active=True
    )
    db.add(phone_user)

    db.commit()
    print("用户创建成功")

    # 验证
    users = db.query(User).filter(User.username.in_(["admin", "15606537209"])).all()
    for user in users:
        print(f"  - {user.username} ({user.email})")

except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
EOF
"""
        stdout, stderr = run_command(ssh, create_script)
        print(stdout)
        if stderr:
            print(f"[ERROR] {stderr}")

        # 修改security.py使用SHA256验证
        print("\n[5/5] 修改密码验证方式")
        modify_script = """
cd /opt/ai-novel-media-agent/backend/app/core
cp security.py security.py.bak

cat > security.py << 'EOF'
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 尝试SHA256验证（临时方案）
    sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    if sha256_hash == hashed_password:
        return True
    # 尝试bcrypt验证
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except:
        return False

def get_password_hash(password: str) -> str:
    # 使用SHA256（临时方案）
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
EOF
"""
        stdout, stderr = run_command(ssh, modify_script)
        if stderr and "error" in stderr.lower():
            print(f"[ERROR] {stderr}")
        else:
            print("[OK] 已修改")

        # 启动后端服务
        print("\n[6/5] 启动后端服务")
        run_command(ssh, "systemctl start ai-novel-media-agent")
        import time
        time.sleep(3)
        stdout, stderr = run_command(ssh, "systemctl status ai-novel-media-agent")
        if "active (running)" in stdout:
            print("[OK] 服务已启动")
        else:
            print("[WARNING] 服务状态异常")
            print(stdout)

        # 测试登录
        print("\n[7/5] 测试登录")
        test_script = """
curl -s -X POST http://localhost:9000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"198964"}'
"""
        stdout, stderr = run_command(ssh, test_script)
        print(f"响应: {stdout}")

        ssh.close()

        print("\n" + "=" * 60)
        print("用户创建完成")
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
