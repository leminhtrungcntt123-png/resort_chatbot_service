import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

def transform_jsonl_to_chunks(input_file: str, output_file: str, chunk_size: int = 500, chunk_overlap: int = 50):
    # 1. Đọc file JSONL và tạo danh sách các document
    documents = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                doc = json.loads(line.strip())
                documents.append(doc)
    
    # 2. Khởi tạo text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # 3. Tạo danh sách các chunk mới
    chunked_documents = []
    for doc in documents:
        content = doc["content"]
        metadata = doc["metadata"]
        
        # Tách nội dung thành các chunk nhỏ hơn
        chunks = text_splitter.split_text(content)
        
        # Tạo một document mới cho mỗi chunk, giữ nguyên metadata
        for i, chunk in enumerate(chunks):
            
            # 🔥 THAY ĐỔI QUAN TRỌNG: ÉP NGỮ CẢNH VÀO ĐẦU MỖI CHUNK
            final_content = chunk
            if metadata.get("category") == "room" and metadata.get("room_number"):
                room_num = metadata.get("room_number")
                floor_num = metadata.get("floor", "Chưa rõ")
                # Gắn thêm nhãn vào đầu mỗi đoạn text bị băm nhỏ
                final_content = f"[Phòng {room_num} - Tầng {floor_num}] {chunk}"
            
            chunked_doc = {
                "doc_id": f"{doc['doc_id']}_chunk_{i}",
                "content": final_content, # Lưu nội dung đã được gắn nhãn
                "metadata": metadata      # Giữ nguyên cục metadata
            }
            chunked_documents.append(chunked_doc)
    
    # 4. Ghi các chunk mới vào file JSONL
    with open(output_file, "w", encoding="utf-8") as f:
        for chunk_doc in chunked_documents:
            f.write(json.dumps(chunk_doc, ensure_ascii=False) + "\n")
    
    print(f"✅ Đã chuyển đổi và ép ngữ cảnh xong! File lưu tại: {output_file}")

if __name__ == "__main__":
    transform_jsonl_to_chunks(
        input_file="data/room_data.jsonl", 
        output_file="data/room_chunks.jsonl"
    )