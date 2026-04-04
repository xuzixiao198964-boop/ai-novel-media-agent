#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证数据库表结构"""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect("104.244.90.202", username="root", password="vDyCuc83NxWw", timeout=30)

    print("[Check] Verifying novels table structure...")
    stdin, stdout, stderr = ssh.exec_command("""
PGPASSWORD='Aa112211' psql -h localhost -U ai_novel -d ai_novel_db -c "
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'novels'
ORDER BY ordinal_position;"
""")
    print(stdout.read().decode())

    print("\n[Check] Checking if table exists in correct schema...")
    stdin, stdout, stderr = ssh.exec_command("""
PGPASSWORD='Aa112211' psql -h localhost -U ai_novel -d ai_novel_db -c "
SELECT schemaname, tablename
FROM pg_tables
WHERE tablename = 'novels';"
""")
    print(stdout.read().decode())

finally:
    ssh.close()
