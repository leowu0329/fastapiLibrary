from fastapi import APIRouter, Depends
from typing import List
from config.database import get_database
from src.modules.books.book_repository import BookRepository
from src.modules.books.book_service import BookService
from src.modules.books.book_entity import BookCreate, BookResponse
from src.middlewares.auth import verify_admin

router = APIRouter(prefix="/books", tags=["圖書與館藏管理"])

def get_book_service(db=Depends(get_database)):
    repo = BookRepository(db)
    return BookService(repo)

@router.post("/", response_model=BookResponse, status_code=201)
async def add_new_book(book_in: BookCreate, service: BookService = Depends(get_book_service), admin=Depends(verify_admin)):
    return await service.add_book(book_in)

@router.get("/", response_model=List[BookResponse])
async def search_books(keyword: str = "", service: BookService = Depends(get_book_service)):
    return await service.query_books(keyword)