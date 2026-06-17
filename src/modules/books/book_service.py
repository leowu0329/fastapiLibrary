from src.modules.books.book_repository import BookRepository
from src.modules.books.book_entity import BookCreate
from fastapi import HTTPException
from typing import List

class BookService:
    def __init__(self, repository: BookRepository):
        self.repo = repository

    async def add_book(self, book_in: BookCreate) -> dict:
        # 實作 ISBN 基礎邏輯檢驗（長度檢驗範例）
        if len(book_in.isbn) not in [10, 13]:
            raise HTTPException(status_code=400, detail="無效的 ISBN 格式，長度須為 10 或 13 碼")
        return await self.repo.create_book(book_in.model_dump())

    async def query_books(self, keyword: str) -> List[dict]:
        return await self.repo.search_books(keyword)