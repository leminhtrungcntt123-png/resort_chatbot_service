import json
import uuid
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

# 1. Khởi tạo Model Hugging Face (Tự động tải về máy lần đầu)
# Model 'all-MiniLM-L6-v2' rất nhẹ, nhanh và phù hợp cho tiếng Việt/Anh cơ bản
print(" đang tải model embedding về máy (miễn phí)...")
model = SentenceTransformer('all-MiniLM-L6-v2') 
VECTOR_SIZE = 384 # Model này tạo ra vector 384 chiều (OpenAI là 1536)

qdrant_client = QdrantClient(url="http://qdrant_db:6333")
COLLECTION_NAME = "resort_management"

def setup_qdrant():
    # THÊM DÒNG NÀY VÀO ĐỂ XÓA BẢN CŨ (Chỉ cần chạy 1 lần rồi xóa dòng này đi cũng được)
    if qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.delete_collection(COLLECTION_NAME)
        print(f"--- Đã xóa Collection cũ (1536) để làm mới ---")

    # Bây giờ nó sẽ tạo mới với size 384 chuẩn Hugging Face
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    # Tạo lại index
    qdrant_client.create_payload_index(COLLECTION_NAME, "metadata.price", "float")
    qdrant_client.create_payload_index(COLLECTION_NAME, "metadata.capacity", "integer")
    print(f"✅ Đã tạo Collection mới: {COLLECTION_NAME} với size {VECTOR_SIZE}")
    
def embed_and_load_chunks(input_file: str, batch_size: int = 100):
    setup_qdrant()
    
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    _count = 0
    for i in range(0, len(all_lines), batch_size):
        batch = all_lines[i : i + batch_size]
        points = []

        # Lấy danh sách nội dung để encode theo batch cho nhanh
        contents = [json.loads(line)["content"] for line in batch]
        # 2. Tạo Vector bằng model local (Không tốn tiền API)
        embeddings = model.encode(contents)

        for j, line in enumerate(batch):
            doc = json.loads(line)
            
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings[j].tolist(), # Chuyển từ numpy array sang list
                payload={
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "doc_id": doc["doc_id"]
                }
            )
            points.append(point)

        # 3. Đẩy lên Qdrant
        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            _count += len(points)
            print(f" Thành công: {_count}/{len(all_lines)} chunks")

if __name__ == "__main__":
    # ĐỔI THÀNH FILE CHUNKS ĐỂ LIÊN KẾT VỚI TRANSFORM.PY
    INPUT_FILE = "data/room_chunks.jsonl" 
    embed_and_load_chunks(INPUT_FILE, batch_size=20)