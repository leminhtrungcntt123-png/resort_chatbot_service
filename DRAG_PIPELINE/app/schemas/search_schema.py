from pydantic import BaseModel, Field
from typing import Optional, List

class DocumentMetadata(BaseModel):
    # Trường bắt buộc duy nhất để phân loại đối tượng: "room", "service", "booking"
    category: str
    source: Optional[str] = "MySQL"
    
    # --- CÁC TRƯỜNG DÀNH CHO PHÒNG (ROOM) & DỊCH VỤ (SERVICE) ---
    name: Optional[str] = None          # Tên phòng (Deluxe...) hoặc tên dịch vụ (Spa...)
    price: Optional[float] = None        # Giá phòng hoặc giá dịch vụ
    capacity: Optional[int] = None       # Sức chứa của phòng
    floor: Optional[int] = None          # Tầng (Bổ sung để đồng bộ bộ lọc tầng)
    room_number: Optional[str] = None    # Số phòng cụ thể

    # --- CÁC TRƯỜNG DÀNH CHO ĐƠN ĐẶT PHÒNG (BOOKING) / KHÁCH HÀNG ---
    customer_name: Optional[str] = None  # Tên khách hàng đặt phòng
    customer_phone: Optional[str] = None # Số điện thoại khách
    check_in: Optional[str] = None       # Ngày nhận phòng
    check_out: Optional[str] = None      # Ngày trả phòng
    status: Optional[str] = None         # Trạng thái đơn (CHECKED_IN, BOOKED...)

# Giữ lại alias để các file cũ gọi RoomMetadata không bị lỗi import
RoomMetadata = DocumentMetadata 

class RoomSearchResult(BaseModel):
    content: str
    metadata: DocumentMetadata
    score: float