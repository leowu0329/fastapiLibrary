from src.modules.users.user_repository import UserRepository
from src.middlewares.auth import create_access_token
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    async def register_user(self, user_in) -> dict:
        existing = await self.repo.get_user_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="此 Email 已被註冊")
        
        # 1. 轉成標準字典
        user_data = user_in.model_dump()
        
        # 2. 強制轉為純文字字串，防止任何物件型態干擾
        raw_password = str(user_in.password)
        
        # 防禦性檢查：印出長度以便在 Uvicorn 終端機除錯 (正式上線可刪除)
        print(f"--- [DEBUG] 準備加密的密碼長度: {len(raw_password)} 碼 ---")
        
        # 3. 進行雜湊
        hashed_password = pwd_context.hash(raw_password)
        
        # 4. 寫回字典
        user_data["password"] = hashed_password
        
        return await self.repo.create_user(user_data)

    async def authenticate_user(self, login_in) -> dict:
        user = await self.repo.get_user_by_email(login_in.email)
        if not user or not pwd_context.verify(str(login_in.password), user["password"]):
            raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
        
        token_data = {"sub": user["email"], "user_id": user["_id"], "role": user["role"]}
        token = create_access_token(token_data)
        return {"access_token": token, "token_type": "bearer"}