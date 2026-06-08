import os
import json
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
    _logger.info("🔥 Bắt đầu trích xuất Dữ liệu Phòng, Dịch vụ, Khách hàng & Bookings...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        with engine.connect() as connection:
            # --- 1. LẤY DỮ LIỆU PHÒNG ---
            room_query = text("""
                SELECT 
                    r.id AS room_id, r.room_number, r.floor_number, r.status AS room_status,
                    rt.type_name, rt.description, rt.price_per_night, rt.capacity
                FROM rooms r
                JOIN room_types rt ON r.room_type_id = rt.id
            """)
            room_result = connection.execute(room_query)
            
            # --- 2. LẤY DỮ LIỆU DỊCH VỤ ---
            service_query = text("SELECT id, service_name, price FROM services")
            service_result = connection.execute(service_query)
            
            # --- 3. LẤY DỮ LIỆU KHÁCH HÀNG & LỊCH SỬ ĐẶT PHÒNG (Bổ sung mới) ---
            # Query này tự động gộp các phòng mà khách đặt, tổng số tiền, hạng VIP và thời gian ở
            booking_customer_query = text("""
                SELECT 
                    b.id AS booking_id,
                    p.full_name AS customer_name,
                    p.phone,
                    p.email,
                    p.vip_tier,
                    p.total_spent,
                    b.check_in_date,
                    b.check_out_date,
                    b.status AS booking_status,
                    GROUP_CONCAT(r.room_number SEPARATOR ', ') AS booked_rooms
                FROM bookings b
                JOIN persons p ON b.customer_id = p.id
                LEFT JOIN booking_rooms br ON b.id = br.booking_id
                LEFT JOIN rooms r ON br.room_id = r.id
                WHERE p.person_type = 'CUSTOMER'
                GROUP BY b.id, p.id
            """)
            booking_customer_result = connection.execute(booking_customer_query)
            
            with open(output_file, "w", encoding="utf-8") as f:
                # ✍️ Ghi dữ liệu Phòng
                for row in room_result.mappings():
                    status_map = {
                        'AVAILABLE': 'Trống (Sẵn sàng đón khách)',
                        'OCCUPIED': 'Đang có khách ở',
                        'MAINTENANCE': 'Đang bảo trì/Sửa chữa'
                    }
                    trang_thai_vn = status_map.get(row['room_status'], 'Chưa rõ trạng thái')
                    so_phong = str(row['room_number'])
                    tang = int(row['floor_number']) if row['floor_number'] is not None else 1

                    doc = {
                        "doc_id": f"room_{so_phong}",
                        "content": f"Phòng số: {so_phong} tại Tầng: {tang}. Loại phòng: {row['type_name']}. Trạng thái hiện tại: {trang_thai_vn}. Sức chứa tối đa: {row['capacity']} người. Giá niêm yết: {float(row['price_per_night'])} VNĐ/đêm.",
                        "metadata": {
                            "category": "room",
                            "name": row['type_name'],
                            "room_number": so_phong,
                            "floor": tang,
                            "price": float(row['price_per_night']),
                            "capacity": row['capacity'],
                            "status": row['room_status']
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                
                # ✍️ Ghi dữ liệu Dịch vụ
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
                    
                # ✍️ Ghi dữ liệu Khách hàng & Bookings (Bổ sung mới)
                status_booking_map = {
                    'PENDING': 'Đang chờ xử lý (Chưa nhận phòng)',
                    'CONFIRMED': 'Đã xác nhận đặt phòng',
                    'CHECKED_IN': 'Đang lưu trú tại resort (Đã Check-in)',
                    'CHECKED_OUT': 'Đã trả phòng và rời đi (Đã Check-out)',
                    'CANCELLED': 'Đã hủy đơn đặt phòng'
                }
                
                count_booking = 0
                for row in booking_customer_result.mappings():
                    trang_thai_booking = status_booking_map.get(row['booking_status'], 'Chưa rõ trạng thái')
                    check_in = str(row['check_in_date'])
                    check_out = str(row['check_out_date'])
                    
                    doc = {
                        "doc_id": f"booking_{row['booking_id']}",
                        # Đoạn content văn bản này được tối ưu từ ngữ để Model Embedding tính toán khoảng cách vector chính xác nhất
                        "content": (
                            f"Khách hàng: {row['customer_name']} (Số điện thoại: {row['phone'] or 'Không có'}, Email: {row['email'] or 'Không có'}). "
                            f"Hạng thành viên: {row['vip_tier']} với tổng chi tiêu: {float(row['total_spent'] or 0):,} VNĐ. "
                            f"Lịch đặt phòng (Mã đơn #{row['booking_id']}): Phòng đăng ký gồm [{row['booked_rooms'] or 'Chưa xếp phòng'}]. "
                            f"Thời gian lưu trú: Từ ngày {check_in} đến ngày {check_out}. "
                            f"Trạng thái đơn đặt phòng: {trang_thai_booking}."
                        ),
                        "metadata": {
                            "category": "booking",
                            "customer_name": row['customer_name'],
                            "vip_tier": row['vip_tier'],
                            "check_in_date": check_in,
                            "check_out_date": check_out,
                            "booking_status": row['booking_status'],
                            "rooms": row['booked_rooms']
                        }
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                    count_booking += 1
                    
        _logger.info(f"🎉 Thành công! Đã đồng bộ thêm {count_booking} bản ghi lịch sử khách hàng vào: {output_file}")
        
    except Exception as e:
        _logger.error(f"❌ Lỗi trích xuất nghiêm trọng: {e}")

if __name__ == "__main__":
    # Đảm bảo đường dẫn này khớp với file INPUT_FILE trong load.py của bạn
    path = os.path.join(DATA_DIR, "room_data.jsonl") 
    extract_all_data_to_jsonl(path)