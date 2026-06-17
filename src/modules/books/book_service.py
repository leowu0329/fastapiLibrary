from src.modules.books.book_entity import BookCreate, BookUpdate
from fastapi import HTTPException, status

class BookService:
    def __init__(self, repository):
        """
        透過控制反轉 (IoC) 注入倉儲層實例
        """
        self.repo = repository

    async def add_book(self, book_in: BookCreate) -> dict:
        """
        商務邏輯：上架新書
        在寫入資料庫前，可在此處擴充 ISBN 查重或重複上架的防護機制。
        """
        # 實作 ISBN 基礎邏輯檢驗（長度檢驗防禦）
        if len(book_in.isbn) not in [10, 13]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="無效的 ISBN 格式，長度必須為 10 碼或 13 碼"
            )
        
        # 將 Pydantic 模型轉換為 Python 字典並傳遞給 Repository
        return await self.repo.create_book(book_in.model_dump())

    async def query_books(self, keyword: str) -> list:
        """
        商務邏輯：多條件關鍵字檢索
        """
        return await self.repo.search_books(keyword)

    async def modify_book(self, book_id: str, book_in: BookUpdate) -> dict:
        """
        商務邏輯：修改圖書資訊/更動庫存
        在此處自動過濾掉前端沒有傳送 (維持 None) 的未修改欄位，實現彈性的局部更新 (PATCH/PUT)。
        """
        # 核心 Clean Code：剔除值為 None 的欄位，避免覆蓋資料庫現有數據
        update_data = {k: v for k, v in book_in.model_dump().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="未提供任何需要更新的圖書欄位資料"
            )
            
        return await self.repo.update_book(book_id, update_data)

    async def remove_book(self, book_id: str) -> bool:
        """
        商務邏輯：報廢/下架圖書
        """
        return await self.repo.delete_book(book_id)