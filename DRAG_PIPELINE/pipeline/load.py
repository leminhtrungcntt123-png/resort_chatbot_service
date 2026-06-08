import json
import uuid
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

# 1. Khởi tạo Model Embedding local
print("🔄 Đang tải/Khởi tạo model embedding 'all-MiniLM-L6-v2'...")
model = SentenceTransformer('all-MiniLM-L6-v2') 
VECTOR_SIZE = 384 

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY")
)
COLLECTION_NAME = "resort_management"

def setup_qdrant():
    # Tự động xóa Collection cũ nếu tồn tại để làm mới hoàn toàn cấu trúc dữ liệu
    if qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.delete_collection(COLLECTION_NAME)
        print(f"--- Đã xóa Collection cũ để đồng bộ dữ liệu G3 mới ---")

    # Tạo mới collection với 384 chiều
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    
    # --- TẠO CÁC PAYLOAD INDEX ĐỂ PHỤC VỤ BỘ LỌC CHÍNH XÁC ---
    # Index phân loại: 'room', 'service', 'booking'
    qdrant_client.create_payload_index(COLLECTION_NAME, "metadata.category", "keyword")
    # Index phục vụ lọc giá phòng / dịch vụ
    qdrant_client.create_payload_index(COLLECTION_NAME, "metadata.price", "float")
    # Index phục vụ lọc sức chứa phòng
    qdrant_client.create_payload_index(COLLECTION_NAME, "metadata.capacity", "integer")
    
    print(f"✅ Đã tạo Collection mới thành công: {COLLECTION_NAME} (Size: {VECTOR_SIZE})")
    
def embed_and_load_chunks(input_file: str, batch_size: int = 100):
    setup_qdrant()
    
    if not os.path.exists(input_file):
        print(f"❌ Thất bại: Không tìm thấy file dữ liệu đầu vào: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    _count = 0
    print(f"🚀 Bắt đầu quá trình Vector hóa và Upload {len(all_lines)} bản ghi lên Cloud...")
    
    for i in range(0, len(all_lines), batch_size):
        batch = all_lines[i : i + batch_size]
        points = []

        # Trích xuất content để chạy Vectorization theo mẻ cho nhanh
        contents = [json.loads(line)["content"] for line in batch]
        embeddings = model.encode(contents)

        for j, line in enumerate(batch):
            doc = json.loads(line)
            
            point = PointStruct(
                id=str(uuid.uuid4()), # Sinh ID ngẫu nhiên không trùng lặp
                vector=embeddings[j].tolist(),
                payload={
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "doc_id": doc["doc_id"]
                }
            )
            points.append(point)

        # Đẩy dữ liệu mẻ này lên Qdrant Cloud
        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            _count += len(points)
            print(f" 🟩 Đã tải lên thành công: {_count}/{len(all_lines)} bản ghi.")

if __name__ == "__main__":
    # SỬA TẠI ĐÂY: Khớp chính xác tên file đầu ra 'room_data.jsonl' của extract.py
    INPUT_FILE = "data/room_data.jsonl" 
    embed_and_load_chunks(INPUT_FILE, batch_size=20)