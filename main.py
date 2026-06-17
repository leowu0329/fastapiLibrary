from fastapi import FastAPI
from contextlib import asynccontextmanager
from config.settings import settings
from config.database import connect_to_mongo, close_mongo_connection
from src.middlewares.logging import audit_logging_middleware
from src.modules.users.user_controller import router as user_router
from src.modules.books.book_controller import router as book_router
from src.modules.circulations.circulation_controller import router as circulation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化資料庫連線
    await connect_to_mongo()
    yield
    # 釋放資源
    await close_mongo_connection()

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

# 掛載審計日誌中間件
app.middleware("http")(audit_logging_middleware)

# 註冊業務核心模組路由
app.include_router(user_router)
app.include_router(book_router)
app.include_router(circulation_router)

@app.get("/", tags=["跟節點"])
async def root():
    return {"status": "healthy", "project": settings.PROJECT_NAME}