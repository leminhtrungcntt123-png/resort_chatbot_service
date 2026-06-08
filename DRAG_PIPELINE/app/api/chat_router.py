import os
import jwt 
from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.rag_service import get_rag_response, generate_answer, analyze_query, retrieve_context
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

security = HTTPBearer()

try:
    JWT_SECRET = os.environ["JWT_SECRET"]
except KeyError:
    logger.critical("LỖI HỆ THỐNG NGHIÊM TRỌNG: Chưa cấu hình biến 'JWT_SECRET' trong file .env!")
    raise RuntimeError("JWT_SECRET is missing. Application cannot start without it.")

JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

def get_role_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        user_role = payload.get("role") 
        if not user_role:
            raise HTTPException(status_code=403, detail="Token không chứa thông tin phân quyền!")
            
        return user_role 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ!")

@router.post("/chat", response_model=ChatResponse, summary="Chat với Trợ lý ảo Resort")
async def chat_with_resort(
    request: ChatRequest, 
    # 🔥 ĐÃ BẬT LẠI: Lấy role thật từ Token do Frontend gửi lên thông qua Header Authorization Bearer
    current_role: str = Depends(get_role_from_token) 
):
    try:
        # 1. Phân tích câu hỏi để lấy bộ lọc (Ví dụ: lọc theo Tầng, loại category='booking' hay 'room')
        filters = analyze_query(request.message)
        
        # 2. Truy vấn lấy ngữ cảnh từ Qdrant (Bao gồm cả Room, Service, Booking tùy theo câu hỏi)
        context_data = retrieve_context(request.message, filters)
        
        # 3. Gọi hàm tạo câu trả lời của LLM dựa trên Ngữ cảnh thu được và Vai trò (Role) của User
        final_result = generate_answer(
            user_message=request.message, 
            related_rooms=context_data, # Biến này map với tham số trong rag_service của bác
            user_role=current_role       # Truyền role thật ('ADMIN', 'MANAGER', 'RECEPTIONIST') vào để LLM giấu/hiện data nhạy cảm
        )
        
        # Trả về đầy đủ các trường cấu trúc cho Frontend nhận diện hành động nút bấm
        return ChatResponse(
            answer=final_result.get("answer", ""),
            suggested_actions=final_result.get("suggested_actions", []),
            related_rooms=context_data
        )
        
    except Exception as e:
        logger.error(f"LỖI CHI TIẾT TẠI BACKEND PYTHON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))