#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试配置保存功能"""

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
    print("=" * 60)
    print("测试配置保存功能")
    print("=" * 60)

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USERNAME, password=PASSWORD)

        # 测试保存API密钥配置
        print("\n[1/3] 测试保存API密钥配置...")
        save_test = """
curl -s -X PUT http://localhost:9000/api/admin/config \
  -H "Content-Type: application/json" \
  -d '{
    "key": "api_keys",
    "value": {
      "openai_api_key": "sk-test-123456",
      "openai_base_url": "https://api.openai.com/v1",
      "video_api_key": "video-key-789",
      "video_api_url": "https://api.video.com",
      "tts_api_key": "tts-key-456",
      "tts_api_url": "https://api.tts.com",
      "image_api_key": "image-key-321",
      "image_api_url": "https://api.image.com"
    },
    "description": "API密钥配置"
  }' | python3 -m json.tool
"""
        status, output, error = execute_ssh_command(ssh, save_test)
        print(output)

        # 验证配置是否保存
        print("\n[2/3] 验证配置是否保存...")
        verify_test = """
curl -s http://localhost:9000/api/admin/config | python3 -c "
import sys, json
data = json.load(sys.stdin)
api_keys = data.get('api_keys', {}).get('value', {})
print('OpenAI Key:', api_keys.get('openai_api_key', 'NOT FOUND'))
print('Video Key:', api_keys.get('video_api_key', 'NOT FOUND'))
print('TTS Key:', api_keys.get('tts_api_key', 'NOT FOUND'))
print('Image Key:', api_keys.get('image_api_key', 'NOT FOUND'))
"
"""
        status, output, error = execute_ssh_command(ssh, verify_test)
        print(output)

        # 检查数据库
        print("\n[3/3] 检查数据库中的配置...")
        db_check = """
cd /opt/ai-novel-media-agent/backend
sqlite3 data/app.db << 'EOFSQL'
.mode column
.headers on
SELECT key, description, updated_at FROM system_configs;
EOFSQL
"""
        status, output, error = execute_ssh_command(ssh, db_check)
        print(output)

        ssh.close()

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n结果说明:")
        print("1. 如果看到 'sk-test-123456' 等测试密钥，说明保存功能正常")
        print("2. 数据库中应该有 api_keys 配置记录")
        print("\n现在可以在前端测试:")
        print("- 访问: http://104.244.90.202/admin")
        print("- 登录: admin / 198964")
        print("- 进入 '系统配置' 页面")
        print("- 填写API密钥并点击 '保存API密钥'")
        print("- 刷新页面验证配置是否保存")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
