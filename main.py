from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import traceback

from config.settings import settings
from config.database import connect_to_mongo, close_mongo_connection
from src.middlewares.logging import audit_logging_middleware
from src.modules.users.user_controller import router as user_router
from src.modules.books.book_controller import router as book_router
from src.modules.circulations.circulation_controller import router as circulation_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

# CORS 標準配置
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 【核心新增】：全域 500 錯誤攔截器，強制補償 CORS 標頭並抓出真兇
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 在後端終端機印出完整的崩潰源頭
    print("====== [❌ 全域攔截到嚴重系統崩潰] ======")
    traceback.print_exc()
    print("========================================")
    
    response = JSONResponse(
        status_code=500,
        content={"detail": f"後端內部伺服器錯誤: {str(exc)}"}
    )
    # 手動強制為 500 錯誤補上 CORS 標頭，防止瀏覽器誤判
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# 掛載審計日誌中間件
app.middleware("http")(audit_logging_middleware)

# 註冊業務路由
app.include_router(user_router)
app.include_router(book_router)
app.include_router(circulation_router)

@app.get("/", tags=["跟節點"])
async def root():
    return {"status": "healthy", "project": settings.PROJECT_NAME}