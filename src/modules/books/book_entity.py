from pydantic import BaseModel, Field

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=10, max_length=13)
    category: str
    stock: int = Field(..., ge=0, description="館藏剩餘庫存量")

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: str = Field(..., alias="_id")

    model_config = {"populate_by_name": True}