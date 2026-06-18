from src.modules.books.book_entity import BookCreate, BookUpdate
from fastapi import HTTPException, status

class BookService:
    def __init__(self, repository):
        """
        透過控制反轉 (IoC) 注入最新規格的 BookRepository 實例
        """
        self.repo = repository

    async def add_book(self, book_in: BookCreate) -> dict:
        """
        商務邏輯：上架新書 (完美對齊 repo.insert)
        """
        if len(book_in.isbn) not in [10, 13]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="無效的 ISBN 格式，長度必須為 10 碼或 13 碼"
            )
        
        # 🔥 核心修正：對齊新版 repo 的方法名稱 insert
        return await self.repo.insert(book_in.model_dump())

    async def query_books(self, keyword: str) -> list:
        """
        商務邏輯：多條件關鍵字檢索 (完美對齊 repo.find_all)
        """
        # 🔥 核心修正：對齊新版 repo 的方法名稱 find_all
        return await self.repo.find_all(keyword)

    async def modify_book(self, book_id: str, book_in: BookUpdate) -> dict:
        """
        商務邏輯：修改圖書資訊/更動庫存 (完美對齊 repo.update)
        """
        update_data = {k: v for k, v in book_in.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="未提供任何需要更新的圖書欄位資料"
            )
            
        # 🔥 核心修正：對齊新版 repo 的方法名稱 update
        return await self.repo.update(book_id, update_data)

    async def remove_book(self, book_id: str) -> bool:
        """
        商務邏輯：報廢/下架圖書 (完美對齊 repo.delete)
        """
        # 🔥 核心修正：對齊新版 repo 的方法名稱 delete
        return await self.repo.delete(book_id)