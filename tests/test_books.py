import pytest
from pydantic import ValidationError
from src.modules.books.book_service import BookService
from src.modules.books.book_entity import BookCreate

@pytest.mark.asyncio
async def test_add_book_invalid_isbn():
    # 測試單元：當 ISBN 長度太短不合規時，驗證 Pydantic 是否會直接在最外層有效拦截
    class MockRepo:
        pass
        
    # 因為 isbn="123" 會在模型初始化時立即爆炸，所以必須將初始化動作直接放入 raises 區塊中
    with pytest.raises(ValidationError) as exc_info:
        BookCreate(
            title="Clean Code", 
            author="Robert C. Martin", 
            isbn="123", # 故意觸發錯誤
            category="Tech", 
            stock=5
        )
    
    # 驗證錯誤訊息是否確實指出是 isbn 欄位長度太短
    assert "isbn" in str(exc_info.value)
    assert "string_too_short" in str(exc_info.value)