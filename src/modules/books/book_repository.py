from bson import ObjectId
from typing import List, Dict, Any

class BookRepository:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["books"]

    def _helper(self, book) -> Dict[str, Any]:
        """強制生成雙向欄位相容字典，完美契合 Pydantic Alias 與前端 JSON 規格"""
        if not book:
            return None
        return {
            "_id": str(book["_id"]),  # 供 FastAPI Pydantic response_model 識別別名
            "id": str(book["_id"]),   # 供前端 React 元件遍歷表格 key={book.id} 讀取
            "title": book["title"],
            "author": book["author"],
            "isbn": book["isbn"],
            "category": book.get("category", "資訊科學"),
            "stock": book.get("stock", 1)
        }

    async def insert(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        book_dict = dict(book_data)
        if "id" in book_dict:
            del book_dict["id"]
        if "_id" in book_dict:
            del book_dict["_id"]
            
        result = await self.collection.insert_one(book_dict)
        inserted_book = await self.collection.find_one({"_id": result.inserted_id})
        return self._helper(inserted_book)

    async def find_all(self, keyword: str = "") -> List[Dict[str, Any]]:
        query = {}
        if keyword:
            query = {
                "$or": [
                    {"title": {"$regex": keyword, "$options": "i"}},
                    {"author": {"$regex": keyword, "$options": "i"}},
                    {"isbn": {"$regex": keyword, "$options": "i"}}
                ]
            }
        
        cursor = self.collection.find(query)
        books = await cursor.to_list(length=1000)
        return [self._helper(b) for b in books]

    async def find_by_id(self, book_id: str) -> Dict[str, Any]:
        if not ObjectId.is_valid(book_id):
            return None
        book = await self.collection.find_one({"_id": ObjectId(book_id)})
        return self._helper(book)

    async def find_by_isbn(self, isbn: str) -> Dict[str, Any]:
        book = await self.collection.find_one({"isbn": isbn})
        return self._helper(book)

    async def update(self, book_id: str, book_data: Dict[str, Any]) -> Dict[str, Any]:
        if not ObjectId.is_valid(book_id):
            return None
            
        clean_data = {k: v for k, v in book_data.items() if k not in ["id", "_id"]}
        
        await self.collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": clean_data}
        )
        updated_book = await self.collection.find_one({"_id": ObjectId(book_id)})
        return self._helper(updated_book)

    async def delete(self, book_id: str) -> bool:
        if not ObjectId.is_valid(book_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(book_id)})
        return result.deleted_count > 0