from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
import logging

logger = logging.getLogger("uvicorn.error")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    logger.info("正在建立 MongoDB Cloud 連線池...")
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.DATABASE_NAME]
    logger.info("MongoDB Cloud 連線成功。")

async def close_mongo_connection():
    logger.info("正在關閉 MongoDB Cloud 連線池...")
    if db_instance.client:
        db_instance.client.close()
    logger.info("MongoDB Cloud 連線已安全中斷。")

def get_database():
    return db_instance.db