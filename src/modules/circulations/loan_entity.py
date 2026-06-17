from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LoanResponse(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    book_id: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str = Field(description="active 或 returned")

    model_config = {"populate_by_name": True}