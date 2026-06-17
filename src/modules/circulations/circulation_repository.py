from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime

class CirculationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.loans = db["loans"]
        self.books = db["books"]

    async def count_active_loans(self, user_id: str) -> int:
        return await self.loans.count_documents({"user_id": user_id, "status": "active"})

    async def find_active_loans_by_user(self, user_id: str) -> List[dict]:
        pipeline = [
            {"$match": {"user_id": user_id, "status": "active"}},
            {"$addFields": {"book_obj_id": {"$toObjectId": "$book_id"}}},
            {
                "$lookup": {
                    "from": "books",
                    "localField": "book_obj_id",
                    "foreignField": "_id",
                    "as": "book_detail"
                }
            },
            {"$unwind": "$book_detail"},
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "book_id": 1,
                    "borrow_date": 1,
                    "due_date": 1,
                    "status": 1,
                    "book_title": "$book_detail.title",
                    "book_author": "$book_detail.author",
                    "book_category": "$book_detail.category"
                }
            }
        ]
        
        cursor = self.loans.aggregate(pipeline)
        results = []
        async for doc in cursor:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            if "id" not in doc and "_id" in doc:
                doc["id"] = doc["_id"]
                
            if isinstance(doc.get("borrow_date"), datetime):
                doc["borrow_date"] = doc["borrow_date"].isoformat()
            if isinstance(doc.get("due_date"), datetime):
                doc["due_date"] = doc["due_date"].isoformat()
            results.append(doc)
        return results

    async def execute_borrow_transaction(self, user_id: str, book_id: str, borrow_date: datetime, due_date: datetime) -> Optional[dict]:
        updated_book = await self.books.find_one_and_update(
            {"_id": ObjectId(book_id), "stock": {"$gt": 0}},
            {"$inc": {"stock": -1}}
        )
        if not updated_book:
            return None 

        loan_doc = {
            "user_id": user_id,
            "book_id": book_id,
            "borrow_date": borrow_date,
            "due_date": due_date,
            "return_date": None,
            "status": "active"
        }
        result = await self.loans.insert_one(loan_doc)
        loan_doc["_id"] = str(result.inserted_id)
        loan_doc["id"] = loan_doc["_id"]
        return loan_doc

    async def find_active_loan(self, loan_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(loan_id):
            return None
        loan = await self.loans.find_one({"_id": ObjectId(loan_id), "status": "active"})
        if loan:
            loan["_id"] = str(loan["_id"])
            loan["id"] = loan["_id"]
        return loan

    async def execute_return_transaction(self, loan_id: str, book_id: str, return_date: datetime) -> bool:
        loan_update = await self.loans.update_one(
            {"_id": ObjectId(loan_id)},
            {"$set": {"status": "returned", "return_date": return_date}}
        )
        if loan_update.modified_count > 0:
            await self.books.update_one(
                {"_id": ObjectId(book_id)},
                {"$inc": {"stock": 1}}
            )
            return True
        return False