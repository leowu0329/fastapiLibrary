from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field(default="reader", description="reader 或 admin")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str = Field(..., alias="_id")

    model_config = {"populate_by_name": True}