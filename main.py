from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.modules.users.user_controller import router as user_router
from src.modules.books.book_controller import router as book_router
from src.modules.circulations.circulation_controller import router as circulation_router
from src.middlewares.logging import audit_logging_middleware
from starlette.middleware.base import BaseHTTPMiddleware

# 初始化 FastAPI 主應用
app = FastAPI(
    title="企業級圖書自動化管理系統後端",
    description="強對接 MongoDB Atlas 雲端叢集 (library_enterprise.books)",
    version="2.0.0"
)

# ==============================================================================
# 1. 核心中間件配置 (Middlewares & CORS)
# ==============================================================================

# 註冊審計與異常日誌追蹤中間件
app.add_middleware(BaseHTTPMiddleware, dispatch=audit_logging_middleware)

# 註冊跨來源資源共享 (CORS) 安全標頭，完美對接 Vite 前端 5173 連線
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# 2. 核心路由表掛載 (Routers)
# ==============================================================================

# 🔥 核心修正：直接在 include_router 時指派 tags，不需再透過 add_api_route 偽造
# 掛載會員登入與註冊模組
app.include_router(user_router, prefix="/users", tags=["讀者認證管理"])

# 掛載全館館藏 CRUD 與 Excel 匯入匯出模組 (內建已設定 tags)
app.include_router(book_router)

# 掛載讀者線上借閱、自主歸還、逾期罰金自動流轉模組 (內建已設定 tags)
app.include_router(circulation_router)

# ==============================================================================
# 3. 系統根目錄健康檢查
# ==============================================================================
@app.get("/", tags=["系統健康檢查"])
async def root_health_check():
    return {
        "status": "healthy",
        "database_target": "mern.v8k6yif.mongodb.net/library_enterprise",
        "message": "圖書管理系統後端 API 服務已完美就緒，通訊暢通。"
    }