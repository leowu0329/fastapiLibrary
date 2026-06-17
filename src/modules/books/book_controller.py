from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_database
from src.modules.books.book_repository import BookRepository
from src.modules.books.book_service import BookService
from src.modules.books.book_entity import BookCreate, BookUpdate, BookResponse
from src.middlewares.auth import verify_admin
from typing import List

router = APIRouter(prefix="/books", tags=["圖書與館藏管理"])

# 依賴注入取得服務層
def get_book_service(db=Depends(get_database)):
    repo = BookRepository(db)
    return BookService(repo)

# --- 1. 上架新書 (僅限管理員) ---
@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_new_book(
    book_in: BookCreate, 
    service: BookService = Depends(get_book_service), 
    admin=Depends(verify_admin)
):
    return await service.add_book(book_in)

# --- 2. 搜尋/獲取所有圖書 (所有人皆可查看) ---
@router.get("/", response_model=List[BookResponse])
async def search_books(
    keyword: str = "", 
    service: BookService = Depends(get_book_service)
):
    return await service.query_books(keyword)

# --- 3. 🔥 核心修正：更新圖書資訊/調整庫存數量 (僅限管理員) ---
@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str, 
    book_in: BookUpdate, 
    service: BookService = Depends(get_book_service), 
    admin=Depends(verify_admin)
):
    """
    管理員專用編輯接口：完美承接前端發送的 book_id 與修改後的數據包。
    """
    updated_book = await service.modify_book(book_id, book_in)
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="編輯失敗，找不到對應的圖書紀錄 ID"
        )
    return updated_book

# --- 4. 報廢/永久下架圖書 (僅限管理員) ---
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str, 
    service: BookService = Depends(get_book_service), 
    admin=Depends(verify_admin)
):
    success = await service.remove_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="下架失敗，找不到對應的圖書紀錄 ID"
        )
    return None