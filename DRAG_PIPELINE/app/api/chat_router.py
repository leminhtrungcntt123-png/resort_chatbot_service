import os
import jwt  # Thư viện giải mã Token (PyJWT)
from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.rag_service import get_rag_response, generate_answer, analyze_query, retrieve_context
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Khởi tạo cơ chế bảo mật Bearer Token để Swagger UI hiện nút "Authorize" (ổ khóa)
security = HTTPBearer()

# Mã bí mật dùng chung để giải mã JWT (Cấu hình trong file .env của Chatbot Service)
# Mã này phải TRÙNG với mã JWT_SECRET của Backend chính
JWT_SECRET = os.getenv("JWT_SECRET", "resort_management_super_secret_key_2024_must_be_at_least_256_bits_long")
JWT_ALGORITHM = "HS256"

def get_role_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Hàm độc lập tự giải mã Token để lấy Quyền (Role) của người dùng"""
    try:
        token = credentials.credentials
        # Giải mã token bằng Secret Key
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Lấy trường 'role' hoặc 'is_admin' được Backend chính đóng gói sẵn trong token
        user_role = payload.get("role") 
        if not user_role:
            raise HTTPException(status_code=403, detail="Token không chứa thông tin phân quyền!")
            
        return user_role # Trả về "admin" hoặc "manager"
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ!")

@router.post("/chat", response_model=ChatResponse, summary="Chat với Trợ lý ảo Resort")
async def chat_with_resort(
    request: ChatRequest, 
    # current_role: str = Depends(get_role_from_token) # Tạm thời đóng để test
    current_role: str = "admin"
):
    try:
        # 1. Phân tích câu hỏi
        filters = analyze_query(request.message)
        
        # 2. Lấy ngữ cảnh phòng từ Qdrant
        related_rooms = retrieve_context(request.message, filters)
        
        # 3. Gọi hàm tạo câu trả lời
        final_answer = generate_answer(
            user_message=request.message, 
            related_rooms=related_rooms, 
            user_role=current_role
        )
        
        # Trả về kết quả (Đã xóa số 1 dư thừa ở đây)
        return ChatResponse(
            answer=final_answer,
            related_rooms=related_rooms
        )
        
    except Exception as e:
        logger.error(f"LỖI CHI TIẾT TẠI BACKEND PYTHON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))