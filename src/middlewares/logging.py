import time
from fastapi import Request
import logging

logger = logging.getLogger("audit")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # 僅示範基礎審計，生產環境可從 request.state 讀取經由 auth 解析出的使用者資訊
    logger.info(f"路徑: {request.url.path} | 方法: {request.method} | 耗時: {process_time:.2f}ms | 狀態碼: {response.status_code}")
    return response