from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_database
from src.modules.circulations.circulation_repository import CirculationRepository
from src.modules.circulations.circulation_service import CirculationService
from src.modules.circulations.loan_entity import LoanResponse
from src.middlewares.auth import get_current_user
from typing import List

router = APIRouter(prefix="/circulations", tags=["借閱與還書管理"])

def get_circulation_service(db=Depends(get_database)):
    repo = CirculationRepository(db)
    return CirculationService(repo)

# --- 核心新增：獲取當前登入讀者的進行中借閱清單 (聯表查詢) ---
@router.get("/my-loans", response_model=List[dict])
async def get_my_active_loans(
    current_user: dict = Depends(get_current_user), 
    service: CirculationService = Depends(get_circulation_service)
):
    """
    讀者專用接口：獲取當前登入用戶所有『未歸還』的圖書詳細明細與截止日期。
    """
    user_id = current_user.get("user_id")
    return await service.get_user_active_loans(user_id)

@router.post("/borrow/{book_id}", response_model=LoanResponse)
async def borrow_book(book_id: str, current_user: dict = Depends(get_current_user), service: CirculationService = Depends(get_circulation_service)):
    user_id = current_user.get("user_id")
    return await service.process_borrow(user_id, book_id)

@router.post("/return/{loan_id}")
async def return_book(loan_id: str, current_user: dict = Depends(get_current_user), service: CirculationService = Depends(get_circulation_service)):
    return await service.process_return(loan_id)