from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

class CirculationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.loans = db["loans"]
        self.books = db["books"]

    async def count_active_loans(self, user_id: str) -> int:
        return await self.loans.count_documents({"user_id": user_id, "status": "active"})

    async def execute_borrow_transaction(self, user_id: str, book_id: str, borrow_date: datetime, due_date: datetime) -> Optional[dict]:
        # 因應 MongoDB Cloud 分散式架構環境，此處採用樂觀鎖/原子化操作確保並行環境下的數據一致性
        # 步驟一：嘗試扣減庫存 (條件為庫存必須大於 0)
        updated_book = await self.books.find_one_and_update(
            {"_id": ObjectId(book_id), "stock": {"$gt": 0}},
            {"$inc": {"stock": -1}}
        )
        if not updated_book:
            return None # 庫存不足或書籍不存在

        # 步驟二：建立借閱歷史明細紀錄
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
        return loan_doc

    async def find_active_loan(self, loan_id: str) -> Optional[dict]:
        if not ObjectId.is_valid(loan_id):
            return None
        loan = await self.loans.find_one({"_id": ObjectId(loan_id), "status": "active"})
        if loan:
            loan["_id"] = str(loan["_id"])
        return loan

    async def execute_return_transaction(self, loan_id: str, book_id: str, return_date: datetime) -> bool:
        # 歸還原子操作：更新紀錄狀態並歸還圖書庫存量
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