import pytest
from src.modules.circulations.circulation_service import CirculationService

class MockCirculationRepository:
    async def count_active_loans(self, user_id: str) -> int:
        return 5 # 直接模擬已達借閱上限 5 本的情境

@pytest.mark.asyncio
async def test_borrow_limit_exceeded():
    repo = MockCirculationRepository()
    service = CirculationService(repo)
    
    with pytest.raises(Exception) as exc_info:
        await service.process_borrow(user_id="user_test_123", book_id="book_test_456")
    assert "借閱上限" in str(exc_info.value)