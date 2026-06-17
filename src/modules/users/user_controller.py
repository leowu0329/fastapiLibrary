from fastapi import APIRouter, Depends
from config.database import get_database
from src.modules.users.user_repository import UserRepository
from src.modules.users.user_service import UserService
from src.modules.users.user_entity import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/users", tags=["用戶與讀者管理"])

def get_user_service(db=Depends(get_database)):
    repo = UserRepository(db)
    return UserService(repo)

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.register_user(user_in)

@router.post("/login")
async def login(login_in: UserLogin, service: UserService = Depends(get_user_service)):
    return await service.authenticate_user(login_in)