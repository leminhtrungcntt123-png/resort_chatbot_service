from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.chat_router import router as chat_router

# 1. Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# 2. KHỞI TẠO APP TRƯỚC (Đây là cái khung nhà)
app = FastAPI(
    title="RAG chatbot",
    description="chatbot ho tro tim kiem phong",
    version="1.0.0"
)

# 3. SAU ĐÓ MỚI THÊM MIDDLEWARE (Sơn tường, lắp cửa)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include router và các route khác
app.include_router(chat_router, prefix="/api")

@app.get("/")
def test():
    return {
        "static": "online",
        "message": "welcome to my chatbot"
    }

logger.info("Run server fastAPI")