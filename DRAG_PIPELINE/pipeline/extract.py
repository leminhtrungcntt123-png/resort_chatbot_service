import json
import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "/app/data" # Hoặc đường dẫn local của bạn
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def extract_all_data_to_jsonl(output_file: str):
    _logger.info("Bắt đầu trích xuất Dữ liệu Phòng & Dịch vụ...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        with engine.connect() as connection:
            # --- 1. LẤY DỮ LIỆU PHÒNG ---
            room_query = text("SELECT id, type_name, description, price_per_night, capacity FROM room_types")
            room_result = connection.execute(room_query)
            
            # --- 2. LẤY DỮ LIỆU DỊCH VỤ ---
            service_query = text("SELECT id, service_name, price FROM services")
            service_result = connection.execute(service_query)
            
            with open(output_file, "w", encoding="utf-8") as f:
                # Ghi dữ liệu Phòng
                for row in room_result.mappings():
                    doc = {
                        "doc_id": f"room_{row['id']}",
                        "content": f"Loại phòng: {row['type_name']}. Chi tiết: {row['description'] or 'Không có mô tả'}. Sức chứa: {row['capacity']} người. Giá: {float(row['price_per_night'])} VNĐ.",
                        "metadata": {
                            "category": "room",
                            "name": row['type_name'],
                            "price": float(row['price_per_night']),
                            "capacity": row['capacity']
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                
                # Ghi dữ liệu Dịch vụ (Thêm vào đây!)
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
                    
        _logger.info(f"Thành công! Đã gom tất cả vào: {output_file}")
        
    except Exception as e:
        _logger.error(f"Lỗi trích xuất: {e}")

if __name__ == "__main__":
    path = os.path.join(DATA_DIR, "room_data.jsonl")
    extract_all_data_to_jsonl(path)