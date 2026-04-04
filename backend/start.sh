#!/bin/bash

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate || source venv/Scripts/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 创建.env文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# 启动服务器
echo "Starting server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
