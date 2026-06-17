from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional

class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["books"]

    async def create_book(self, book_data: dict) -> dict:
        result = await self.collection.insert_one(book_data)
        book_data["_id"] = str(result.inserted_id)
        book_data["id"] = book_data["_id"]
        return book_data

    async def search_books(self, keyword: str) -> List[dict]:
        query = {}
        if keyword:
            query = {"$or": [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"author": {"$regex": keyword, "$options": "i"}},
                {"isbn": keyword}
            ]}
            
        cursor = self.collection.find(query)
        books = []
        async for doc in cursor:
            # 核心清洗：強制將 BSON ObjectId 轉為純文字字串，並雙向指派 id 與 _id
            doc["id"] = str(doc["_id"])
            doc["_id"] = doc["id"]
            books.append(doc)
        return books

    async def update_book(self, book_id: str, update_data: dict) -> Optional[dict]:
        if not ObjectId.is_valid(book_id):
            return None
            
        await self.collection.update_one(
            {"_id": ObjectId(book_id)}, 
            {"$set": update_data}
        )
        
        doc = await self.collection.find_one({"_id": ObjectId(book_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            doc["_id"] = doc["id"]
        return doc

    async def delete_book(self, book_id: str) -> bool:
        if not ObjectId.is_valid(book_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count > 0