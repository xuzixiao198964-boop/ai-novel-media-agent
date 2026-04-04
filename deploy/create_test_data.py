#!/usr/bin/env python3
"""创建管理员账号和测试数据"""
import paramiko
import json

# 服务器配置
SERVER = "104.244.90.202"
USERNAME = "root"
PASSWORD = "vDyCuc83NxWw"
PORT = 22

def create_test_data():
    """创建测试数据"""
    print("开始创建测试数据...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"连接服务器 {SERVER}...")
        ssh.connect(SERVER, port=PORT, username=USERNAME, password=PASSWORD)

        # 创建管理员账号
        print("\n1. 创建管理员账号...")
        create_admin_cmd = """
cd /opt/ai-novel-media-agent/backend && python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/ai-novel-media-agent/backend')

from app.database import SessionLocal
from app.models import User
import bcrypt

db = SessionLocal()

# 检查管理员是否存在
admin = db.query(User).filter(User.username == "admin").first()
if admin:
    print("管理员账号已存在")
else:
    # 创建管理员
    hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hashed.decode('utf-8')
    )
    db.add(admin)
    db.commit()
    print("管理员账号创建成功: admin / admin123")

db.close()
EOF
"""
        stdin, stdout, stderr = ssh.exec_command(create_admin_cmd)
        print(stdout.read().decode('utf-8'))
        err = stderr.read().decode('utf-8')
        if err:
            print("错误:", err)

        # 创建测试小说数据
        print("\n2. 创建测试小说数据...")
        create_novels_cmd = """
cd /opt/ai-novel-media-agent/backend && python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/ai-novel-media-agent/backend')

from app.database import SessionLocal
from app.models import User, Novel
from datetime import datetime

db = SessionLocal()

# 获取测试用户（通过username查询）
user = db.query(User).filter(User.username == "15606537209").first()
if not user:
    print("测试用户不存在，跳过创建小说")
else:
    # 创建3本测试小说
    novels_data = [
        {
            "title": "都市修仙传",
            "genre": "都市修仙",
            "outline": "一个普通上班族意外获得修仙系统，在都市中开启修仙之路",
            "content": "第一章 意外觉醒\\n\\n李明是一个普通的上班族...",
            "status": "completed",
            "is_public": True,
            "rating": 4.5,
            "view_count": 1250
        },
        {
            "title": "星际争霸录",
            "genre": "科幻",
            "outline": "人类进入星际时代，主角驾驶机甲征战星海",
            "content": "序章 星海征途\\n\\n公元2500年，人类文明已经...",
            "status": "in_progress",
            "is_public": True,
            "rating": 4.8,
            "view_count": 2100
        },
        {
            "title": "古武宗师",
            "genre": "武侠",
            "outline": "一代宗师重生归来，重振古武门派",
            "content": "第一回 重生\\n\\n江湖风云再起...",
            "status": "draft",
            "is_public": False,
            "rating": 0.0,
            "view_count": 0
        }
    ]

    for novel_data in novels_data:
        existing = db.query(Novel).filter(Novel.title == novel_data["title"]).first()
        if not existing:
            novel = Novel(
                user_id=user.id,
                **novel_data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(novel)
            print(f"创建小说: {novel_data['title']}")
        else:
            print(f"小说已存在: {novel_data['title']}")

    db.commit()
    print(f"\\n测试小说创建完成")

db.close()
EOF
"""
        stdin, stdout, stderr = ssh.exec_command(create_novels_cmd)
        print(stdout.read().decode('utf-8'))
        err = stderr.read().decode('utf-8')
        if err:
            print("错误:", err)

        # 创建测试任务数据
        print("\n3. 创建测试任务数据...")
        create_tasks_cmd = """
cd /opt/ai-novel-media-agent/backend && python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/ai-novel-media-agent/backend')

from app.database import SessionLocal
from app.models import User, Task
from datetime import datetime

db = SessionLocal()

user = db.query(User).filter(User.username == "15606537209").first()
if not user:
    print("测试用户不存在，跳过创建任务")
else:
    tasks_data = [
        {
            "task_type": "novel",
            "status": "completed",
            "result_data": {"novel_id": 1, "title": "都市修仙传"}
        },
        {
            "task_type": "novel",
            "status": "running",
            "result_data": {}
        },
        {
            "task_type": "video",
            "status": "pending",
            "result_data": {}
        }
    ]

    for task_data in tasks_data:
        task = Task(
            user_id=user.id,
            **task_data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(task)

    db.commit()
    print("测试任务创建完成")

db.close()
EOF
"""
        stdin, stdout, stderr = ssh.exec_command(create_tasks_cmd)
        print(stdout.read().decode('utf-8'))
        err = stderr.read().decode('utf-8')
        if err:
            print("错误:", err)

        print("\n[OK] 测试数据创建完成！")
        print("\n账号信息:")
        print("  管理员: admin / admin123")
        print("  测试用户: 15606537209 / 198964")
        print("\n访问地址:")
        print(f"  管理后台: http://{SERVER}:8001/")
        print(f"  用户端: http://{SERVER}:8000/")

    except Exception as e:
        print(f"[ERROR] 创建失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    create_test_data()
