from pydantic import BaseModel, Field
from typing import List, Optional
from .search_schema import RoomSearchResult

# --- 1. ĐỊNH NGHĨA CẤU TRÚC NÚT BẤM (THÊM MỚI) ---
class ActionItem(BaseModel):
    label: str
    action: str
    payload: str

# --- 2. NHẬN CÂU HỎI TỪ NGƯỜI DÙNG (Giữ nguyên của bạn) ---
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None       # Đã thêm giá trị mặc định, không sợ thiếu
    session_id: Optional[str] = None   # Đã thêm giá trị mặc định

# --- 3. TRẢ VỀ CÂU TRẢ LỜI CỦA AI (CẬP NHẬT) ---
class ChatResponse(BaseModel):
    answer: str  # Câu trả lời từ LLM (Groq/OpenAI)
    
    # 🔥 ĐÂY LÀ DÒNG CHÌA KHÓA: Báo cho FastAPI biết là có trả về nút bấm
    suggested_actions: Optional[List[ActionItem]] = [] 
    
    related_rooms: List[RoomSearchResult]  # Danh sách các phòng tìm thấy trong Qdrant