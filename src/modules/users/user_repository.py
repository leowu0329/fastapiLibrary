from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional  # 補上這行，宣告型別必備

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        user = await self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def create_user(self, user_data: dict) -> dict:
        result = await self.collection.insert_one(user_data)
        user_data["_id"] = str(result.inserted_id)
        return user_data