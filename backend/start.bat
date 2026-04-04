@echo off

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo Installing dependencies...
pip install -r requirements.txt

REM 创建.env文件（如果不存在）
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

REM 启动服务器
echo Starting server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
