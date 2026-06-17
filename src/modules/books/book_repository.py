from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional

class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["books"]

    async def create_book(self, book_data: dict) -> dict:
        result = await self.collection.insert_one(book_data)
        book_data["_id"] = str(result.inserted_id)
        return book_data

    async def find_by_id(self, book_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(book_id):
            return None
        book = await self.collection.find_one({"_id": ObjectId(book_id)})
        if book:
            book["_id"] = str(book["_id"])
        return book

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
            doc["_id"] = str(doc["_id"])
            books.append(doc)
        return books