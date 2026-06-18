from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

#  核心修正：不再於此處硬編碼連線資訊
# 直接從 config/settings.py 讀取已經處理過環境變數的 settings 物件
# 確保你在根目錄的 .env 檔案中已設定 MONGODB_URL 與 DATABASE_NAME
client = AsyncIOMotorClient(settings.MONGODB_URL)

def get_database():
    """
    FastAPI 依賴注入：確保每一次路由調用，都拿得到指向雲端「library_enterprise」的資料庫實例。
    """
    return client[settings.DATABASE_NAME]

def get_collection(collection_name: str):
    """
    快速獲取指定集合工具
    """
    return client[settings.DATABASE_NAME][collection_name]