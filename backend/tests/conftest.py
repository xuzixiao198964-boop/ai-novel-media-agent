"""
测试配置和fixtures
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# 导入应用模块（待Agent创建后）
# from app.database import Base
# from app.main import app
# from app.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    创建测试数据库会话
    使用内存SQLite数据库
    """
    # 创建内存数据库
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 创建所有表
    # Base.metadata.create_all(bind=engine)

    # 创建会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(test_db: Session):
    """创建测试用户"""
    # from app.models import User
    # user = User(
    #     username="testuser",
    #     email="test@example.com",
    #     password_hash="hashed_password",
    #     balance=100.0
    # )
    # test_db.add(user)
    # test_db.commit()
    # test_db.refresh(user)
    # return user
    pass


@pytest.fixture
def mock_llm_response():
    """Mock LLM API响应"""
    return "这是一个模拟的LLM响应"


@pytest.fixture
def mock_task_config():
    """Mock任务配置"""
    return {
        "task_type": "novel_only",
        "novel_config": {
            "length_type": "short",
            "genre": "male",
            "sub_genre": "xuanhuan"
        }
    }


# 集成测试fixtures
@pytest.fixture(scope="session")
async def test_client():
    """创建测试客户端"""
    # from httpx import AsyncClient
    # async with AsyncClient(app=app, base_url="http://test") as client:
    #     yield client
    pass


@pytest.fixture(scope="session")
def docker_compose_file():
    """指定docker-compose测试文件"""
    return "deploy/docker-compose.test.yml"
