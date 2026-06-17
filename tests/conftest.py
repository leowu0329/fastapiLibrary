import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config.database import db_instance

# 使用新版 pytest-asyncio 規範設定非函式級別 (session) 的異步事件迴圈
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def mock_db_setup():
    # 測試時重新導向至測試用沙盒資料庫，徹底隔離雲端資料
    test_client = AsyncIOMotorClient("mongodb://localhost:27017")
    db_instance.client = test_client
    db_instance.db = test_client["test_library_db"]
    yield
    try:
        await test_client.drop_database("test_library_db")
    except Exception:
        pass
    test_client.close()