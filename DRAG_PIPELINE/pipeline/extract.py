import json
import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "/app/data" 
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL, connect_args={'charset': 'utf8mb4'})

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def extract_all_data_to_jsonl(output_file: str):
    _logger.info("Bắt đầu trích xuất Dữ liệu Phòng cụ thể & Dịch vụ theo DB G3...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        with engine.connect() as connection:
            # --- 1. LẤY DỮ LIỆU PHÒNG (SỬ DỤNG ĐÚNG CHUẨN floor_number TỪ DB CỦA BẠN) ---
            room_query = text("""
                SELECT 
                    r.id AS room_id,
                    r.room_number,
                    r.floor_number,
                    r.status AS room_status,
                    rt.type_name,
                    rt.description,
                    rt.price_per_night,
                    rt.capacity
                FROM rooms r
                JOIN room_types rt ON r.room_type_id = rt.id
            """)
            room_result = connection.execute(room_query)
            
            # --- 2. LẤY DỮ LIỆU DỊCH VỤ ---
            service_query = text("SELECT id, service_name, price FROM services")
            service_result = connection.execute(service_query)
            
            with open(output_file, "w", encoding="utf-8") as f:
                # Ghi dữ liệu từng Phòng cụ thể
                for row in room_result.mappings():
                    # Dịch trạng thái Enum sang Tiếng Việt cho AI hiểu sâu sắc hơn
                    status_map = {
                        'AVAILABLE': 'Trống (Sẵn sàng đón khách)',
                        'OCCUPIED': 'Đang có khách ở',
                        'MAINTENANCE': 'Đang bảo trì/Sửa chữa'
                    }
                    trang_thai_vn = status_map.get(row['room_status'], 'Chưa rõ trạng thái')
                    print(f"=== TEST FONT TỪ DB: {row['type_name']} - {trang_thai_vn} ===")
                    # Ép kiểu dữ liệu an toàn
                    so_phong = str(row['room_number'])
                    tang = int(row['floor_number']) if row['floor_number'] is not None else 1

                    doc = {
                        # SỬA TẠI ĐÂY: Dùng trực tiếp số phòng (ví dụ: room_101) làm doc_id để AI không bị loạn chữ "Phòng 1"
                        "doc_id": f"room_{so_phong}",
                        # Chuẩn hóa chuỗi văn bản ngữ cảnh cho Embedding quét tốt nhất
                        "content": f"Phòng số: {so_phong} tại Tầng: {tang}. Loại phòng: {row['type_name']}. Trạng thái hiện tại: {trang_thai_vn}. Mô tả chi tiết: {row['description'] or 'Không có mô tả'}. Sức chứa tối đa: {row['capacity']} người. Giá niêm yết: {float(row['price_per_night'])} VNĐ/đêm.",
                        "metadata": {
                            "category": "room",
                            "name": row['type_name'],
                            "room_number": so_phong,
                            "floor": tang, # Trường này đồng bộ với hàm getattr(meta, 'floor') trong rag_service
                            "price": float(row['price_per_night']),
                            "capacity": row['capacity'],
                            "status": row['room_status']
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                
                # Ghi dữ liệu Dịch vụ
                for row in service_result.mappings():
                    doc = {
                        "doc_id": f"service_{row['id']}",
                        "content": f"Dịch vụ: {row['service_name']}. Giá: {float(row['price'])} VNĐ.",
                        "metadata": {
                            "category": "service",
                            "name": row['service_name'],
                            "price": float(row['price'])
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    
        _logger.info(f"Thành công! Toàn bộ phòng ({room_result.rowcount} phòng) đã được đồng bộ vào: {output_file}")
        
    except Exception as e:
        _logger.error(f"Lỗi trích xuất nghiêm trọng: {e}")

if __name__ == "__main__":
    path = os.path.join(DATA_DIR, "room_data.jsonl")
    extract_all_data_to_jsonl(path)