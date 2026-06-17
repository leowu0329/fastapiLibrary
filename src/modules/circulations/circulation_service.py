from src.modules.circulations.circulation_repository import CirculationRepository
from src.utils.date_helper import DateHelper
from fastapi import HTTPException

class CirculationService:
    def __init__(self, repository: CirculationRepository):
        self.repo = repository
        self.borrow_limit = 5 # 讀者借閱數量限制上限

    async def process_borrow(self, user_id: str, book_id: str) -> dict:
        # 1. 檢查讀者未歸還之借閱上限
        active_count = await self.repo.count_active_loans(user_id)
        if active_count >= self.borrow_limit:
            raise HTTPException(status_code=400, detail=f"已達借閱上限（最高 {self.borrow_limit} 本），請先歸還舊書")

        # 2. 進行扣減庫存與建立紀錄的整合封裝操作
        borrow_date = DateHelper.get_current_time()
        due_date = DateHelper.calculate_due_date(days=14)
        
        loan_record = await self.repo.execute_borrow_transaction(user_id, book_id, borrow_date, due_date)
        if not loan_record:
            raise HTTPException(status_code=400, detail="書籍庫存不足，無法辦理借閱")
            
        return loan_record

    async def process_return(self, loan_id: str) -> dict:
        loan = await self.repo.find_active_loan(loan_id)
        if not loan:
            raise HTTPException(status_code=404, detail="找不到對應的進行中借閱紀錄")

        return_date = DateHelper.get_current_time()
        overdue_days = DateHelper.calculate_overdue_days(loan["due_date"])
        fine = DateHelper.calculate_fine(overdue_days, fine_per_day=5)

        success = await self.repo.execute_return_transaction(loan_id, loan["book_id"], return_date)
        if not success:
            raise HTTPException(status_code=500, detail="歸還作業因資料衝突失敗")

        return {
            "message": "還書成功",
            "overdue_days": overdue_days,
            "fine": fine
        }