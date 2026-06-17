from pydantic import BaseModel, Field
from typing import Optional

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    isbn: str = Field(..., min_length=10, max_length=13)
    category: str
    stock: int = Field(..., ge=0)

class BookCreate(BookBase):
    pass

# 🔥 核心補強：定義專門給 PUT 路由使用的更新實體模型
# 內部所有欄位皆設為 Optional，這樣管理員只修改庫存時，其他未填寫的欄位才不會爆錯
class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)

class BookResponse(BookBase):
    id: str = Field(..., alias="_id")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }