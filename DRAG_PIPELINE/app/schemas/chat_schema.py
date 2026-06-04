from pydantic import BaseModel, Field
from typing import List, Optional
from .search_schema import RoomSearchResult

# Nhận câu hỏi từ người dùng (Input)
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None       #  Đã thêm giá trị mặc định, không sợ thiếu
    session_id: Optional[str] = None   #  Đã thêm giá trị mặc định

# Trả về câu trả lời của AI (Output)
class ChatResponse(BaseModel):
    answer: str  # Câu trả lời từ LLM (Groq/OpenAI)
    related_rooms: List[RoomSearchResult]  # Danh sách các phòng tìm thấy trong Qdrant