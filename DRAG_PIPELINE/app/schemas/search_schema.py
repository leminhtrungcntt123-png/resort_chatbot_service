from pydantic import BaseModel, Field
from typing import Optional

class DocumentMetadata(BaseModel):
    category: str
    name: str
    price: float
    capacity: Optional[int] = None
    source: Optional[str] = "MySQL"

# Thêm dòng này để "alias" lại cái tên cũ, giúp hệ thống không bị crash
RoomMetadata = DocumentMetadata 

class RoomSearchResult(BaseModel):
    content: str
    metadata: DocumentMetadata
    score: float