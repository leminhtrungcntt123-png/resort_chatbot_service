-- ============================================================
--  RESORT MANAGEMENT - DATABASE SCRIPT
--  Phiên bản G3: Đồng bộ Enum values với Java Entity
-- ============================================================

DROP DATABASE IF EXISTS resort_management;
CREATE DATABASE resort_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE resort_management;
SET NAMES 'utf8mb4';
-- ============================================================
-- 1. BẢNG ĐỘC LẬP & LỚP CHA
-- ============================================================

CREATE TABLE room_types (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    type_name       VARCHAR(100) NOT NULL,
    description     TEXT,
    price_per_night DECIMAL(18,2) NOT NULL CHECK (price_per_night > 0),
    capacity        INT NOT NULL CHECK (capacity > 0),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE persons (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    phone          VARCHAR(20),
    email          VARCHAR(100),
    person_type    VARCHAR(31) NOT NULL,
    loyalty_points INT DEFAULT 0,
    position       VARCHAR(100),
    salary         DECIMAL(18,2),
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)          -- ← thêm index
);

CREATE TABLE services (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    price        DECIMAL(18,2) NOT NULL CHECK (price > 0),
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. BẢNG CÓ KHÓA NGOẠI
-- ============================================================

CREATE TABLE rooms (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    room_number  VARCHAR(20) NOT NULL UNIQUE,
    room_type_id INT NOT NULL,
    floor_number INT,
    -- ← Đổi sang Enum values: AVAILABLE | OCCUPIED | MAINTENANCE
    status       VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE'
                 CHECK (status IN ('AVAILABLE', 'OCCUPIED', 'MAINTENANCE')),
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id),
    INDEX idx_room_type (room_type_id)
);

CREATE TABLE bookings (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    customer_id    INT NOT NULL,
    check_in_date  DATE NOT NULL,
    check_out_date DATE NOT NULL,
    -- ← Đổi sang Enum values: PENDING | CONFIRMED | CHECKED_IN | CHECKED_OUT | CANCELLED
    status         VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                   CHECK (status IN ('PENDING','CONFIRMED','CHECKED_IN','CHECKED_OUT','CANCELLED')),
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES persons(id),
    CHECK (check_out_date > check_in_date),
    INDEX idx_customer (customer_id),
    INDEX idx_status (status),
    INDEX idx_check_in_date (check_in_date)  -- ← thêm index
);

-- ============================================================
-- 3. BẢNG TRUNG GIAN & PHỤ TRỢ
-- ============================================================

CREATE TABLE booking_rooms (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    room_id    INT NOT NULL,
    price      DECIMAL(18,2) NOT NULL,  -- ← Đổi từ DOUBLE sang DECIMAL
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id)    REFERENCES rooms(id)    ON DELETE CASCADE
);

CREATE TABLE booking_services (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    service_id INT NOT NULL,
    quantity   INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

CREATE TABLE payments (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    booking_id     INT NOT NULL UNIQUE,
    amount         DECIMAL(18,2) NOT NULL CHECK (amount >= 0),
    -- ← Đã thêm QR vào Enum values
    payment_method VARCHAR(10) NOT NULL
                   CHECK (payment_method IN ('CASH', 'CARD', 'QR')),
    -- ← Enum values: PENDING | PAID | FAILED
    payment_status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                   CHECK (payment_status IN ('PENDING', 'PAID', 'FAILED')),
    payment_date   DATETIME NULL,
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    INDEX idx_booking_payment (booking_id),
    INDEX idx_payment_status  (payment_status),
    INDEX idx_payment_date    (payment_date)
);

-- ============================================================
-- 4. BẢNG USERS (mới - chuẩn bị cho G4 Spring Security)
-- ============================================================

CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,      -- BCrypt hash
    role        VARCHAR(20)  NOT NULL DEFAULT 'RECEPTIONIST'
                CHECK (role IN ('ADMIN', 'MANAGER', 'RECEPTIONIST')),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    employee_id INT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES persons(id) ON DELETE SET NULL,
    INDEX idx_username (username)
);

-- ============================================================
-- 5. DỮ LIỆU MẪU
-- ============================================================

INSERT INTO room_types (type_name, description, price_per_night, capacity) VALUES
('Standard City View',  'Phòng tiêu chuẩn hướng thành phố',           600000,   2),
('Standard Ocean View', 'Phòng tiêu chuẩn hướng biển',                 750000,   2),
('Deluxe City View',    'Phòng cao cấp hướng thành phố',               1100000,  2),
('Deluxe Ocean View',   'Phòng cao cấp hướng biển',                    1300000,  2),
('Suite Ocean Front',   'Phòng Suite mặt biển cao cấp',                2800000,  4),
('Family Garden',       'Phòng gia đình hướng vườn',                   1700000,  5),
('Couple Romance',      'Phòng lãng mạn cho cặp đôi',                  850000,   2),
('Villa 2 Bedrooms',    'Biệt thự 2 phòng ngủ',                        7000000,  4),
('Bungalow Ocean',      'Nhà gỗ hướng biển',                           1600000,  2),
('Presidential Suite',  'Phòng Tổng thống siêu cấp',                   15000000, 6);

INSERT INTO services (service_name, price) VALUES
('Ăn tối hải sản', 850000),    ('Đưa đón sân bay', 400000),     ('Thuê xe máy 1 ngày', 150000),
('Thuê xe ô tô 4 chỗ', 800000),('Tour đảo nửa ngày', 650000),   ('Tour lặn ngắm san hô', 900000),
('Spa VIP', 1200000),           ('Xông hơi đá muối', 350000),    ('Massage Thái', 600000),
('Buffet BBQ Tối', 550000),     ('Set ăn trưa gia đình', 450000),('Phục vụ ăn tại phòng', 150000),
('Trang trí phòng trăng mật', 1000000), ('Bánh kem sinh nhật', 350000), ('Hoa tươi tại phòng', 250000),
('Thuê lều trại', 400000),      ('BBQ bãi biển', 700000),        ('Vé công viên nước', 250000),
('Sân Tennis 1 giờ', 200000),   ('Sân Golf mini', 500000),       ('Dịch vụ trông trẻ', 150000),
('Giặt ủi nhanh', 120000),      ('Đánh giày', 50000),            ('Minibar Full Set', 800000),
('Thuê Kayak 1 giờ', 200000),   ('Chèo SUP', 250000),            ('Cano siêu tốc', 1500000),
('Yoga buổi sáng', 100000),     ('Lớp nấu ăn', 400000),          ('Lớp pha chế', 450000),
('Chụp ảnh kỷ niệm', 1200000),  ('Trà chiều', 250000),           ('Thức uống Welcome', 50000),
('Dọn phòng thêm', 100000),     ('Mượn bàn ủi', 20000),          ('Thuê loa kéo', 300000),
('Gói tổ chức tiệc', 5000000),  ('Hội trường 4h', 3000000),      ('Hội trường 8h', 5500000),
('Dịch vụ y tế', 200000);

INSERT INTO persons (full_name, phone, email, person_type, loyalty_points, position, salary) VALUES
('Nguyen Van Mot',    '0911111111', 'mot@gmail.com',        'CUSTOMER', 10,   NULL, NULL),
('Tran Thi Hai',      '0922222222', 'hai@gmail.com',        'CUSTOMER', 20,   NULL, NULL),
('Le Van Ba',         '0933333333', 'ba@gmail.com',         'CUSTOMER', 5,    NULL, NULL),
('Pham Thi Bon',      '0944444444', 'bon@gmail.com',        'CUSTOMER', 150,  NULL, NULL),
('Hoang Van Nam',     '0955555555', 'nam@gmail.com',        'CUSTOMER', 300,  NULL, NULL),
('Vu Thi Sau',        '0966666666', 'sau@gmail.com',        'CUSTOMER', 0,    NULL, NULL),
('Vo Van Bay',        '0977777777', 'bay@gmail.com',        'CUSTOMER', 50,   NULL, NULL),
('Phan Thi Tam',      '0988888888', 'tam@gmail.com',        'CUSTOMER', 80,   NULL, NULL),
('Dang Van Chin',     '0999999991', 'chin@gmail.com',       'CUSTOMER', 0,    NULL, NULL),
('Bui Thi Muoi',      '0910101010', 'muoi@gmail.com',       'CUSTOMER', 200,  NULL, NULL),
('Do Van Muoi Mot',   '0911223344', 'mmot@gmail.com',       'CUSTOMER', 40,   NULL, NULL),
('Ly Thi Muoi Hai',   '0922334455', 'mhai@gmail.com',       'CUSTOMER', 60,   NULL, NULL),
('Ngo Van Muoi Ba',   '0933445566', 'mba@gmail.com',        'CUSTOMER', 10,   NULL, NULL),
('Dinh Thi Muoi Bon', '0944556677', 'mbon@gmail.com',       'CUSTOMER', 0,    NULL, NULL),
('Dao Van Muoi Lam',  '0955667788', 'mlam@gmail.com',       'CUSTOMER', 350,  NULL, NULL),
('Trinh Thi Muoi Sau','0966778899', 'msau@gmail.com',       'CUSTOMER', 15,   NULL, NULL),
('Truong Van Muoi Bay','0977889900','mbay@gmail.com',        'CUSTOMER', 25,   NULL, NULL),
('Lam Thi Muoi Tam',  '0988990011', 'mtam@gmail.com',       'CUSTOMER', 70,   NULL, NULL),
('Mai Van Muoi Chin', '0999001122', 'mchin@gmail.com',       'CUSTOMER', 0,    NULL, NULL),
('Phung Thi Hai Muoi','0912312312', 'hmuoi@gmail.com',       'CUSTOMER', 100,  NULL, NULL),
('Kieu Van Hai Mot',  '0923423423', 'hmot@gmail.com',        'CUSTOMER', 5,    NULL, NULL),
('Chau Thi Hai Hai',  '0934534534', 'hhai@gmail.com',        'CUSTOMER', 20,   NULL, NULL),
('Thach Van Hai Ba',  '0945645645', 'hba@gmail.com',         'CUSTOMER', 40,   NULL, NULL),
('To Thi Hai Bon',    '0956756756', 'hbon@gmail.com',        'CUSTOMER', 0,    NULL, NULL),
('Mac Van Hai Lam',   '0967867867', 'hlam@gmail.com',        'CUSTOMER', 500,  NULL, NULL),
('Khong Thi Hai Sau', '0978978978', 'hsau@gmail.com',        'CUSTOMER', 30,   NULL, NULL),
('Ton Van Hai Bay',   '0989089089', 'hbay@gmail.com',        'CUSTOMER', 10,   NULL, NULL),
('Giang Thi Hai Tam', '0990190190', 'htam@gmail.com',        'CUSTOMER', 0,    NULL, NULL),
('Ha Van Hai Chin',   '0913413413', 'hchin@gmail.com',       'CUSTOMER', 60,   NULL, NULL),
('Chung Thi Ba Muoi', '0924524524', 'bmuoi@gmail.com',       'CUSTOMER', 120,  NULL, NULL),
('Nguyen Quoc Bao',   '0811112222', 'bao.nv@resort.com',    'EMPLOYEE', NULL, 'Quản lý Nhân sự',   25000000),
('Tran Kieu An',      '0822223333', 'an.tk@resort.com',     'EMPLOYEE', NULL, 'Trưởng Lễ tân',     15000000),
('Le Thanh Binh',     '0833334444', 'binh.lt@resort.com',   'EMPLOYEE', NULL, 'Kế toán',           12000000),
('Pham Tuan Dat',     '0844445555', 'dat.pt@resort.com',    'EMPLOYEE', NULL, 'Bảo vệ',            7000000),
('Hoang Thu Ha',      '0855556666', 'ha.ht@resort.com',     'EMPLOYEE', NULL, 'Buồng phòng',       6500000),
('Vu Duc Thang',      '0866667777', 'thang.vd@resort.com',  'EMPLOYEE', NULL, 'Đầu bếp',           18000000),
('Vo My Linh',        '0877778888', 'linh.vm@resort.com',   'EMPLOYEE', NULL, 'Lễ tân Ca tối',     8500000),
('Phan Nhat Minh',    '0888889999', 'minh.pn@resort.com',   'EMPLOYEE', NULL, 'Bảo trì',           9000000),
('Dang Huu Phuc',     '0899990000', 'phuc.dh@resort.com',   'EMPLOYEE', NULL, 'IT Support',        14000000),
('Bui Ngoc Chau',     '0810102020', 'chau.bn@resort.com',   'EMPLOYEE', NULL, 'Sale Marketing',    13000000);

-- ← Đổi toàn bộ tiếng Việt → Enum values
INSERT INTO rooms (room_number, room_type_id, floor_number, status) VALUES
('101', 1, 1, 'AVAILABLE'),  ('102', 1, 1, 'OCCUPIED'),    ('103', 1, 1, 'AVAILABLE'),  ('104', 1, 1, 'MAINTENANCE'),
('105', 2, 1, 'AVAILABLE'),  ('106', 2, 1, 'AVAILABLE'),   ('107', 2, 1, 'OCCUPIED'),   ('108', 2, 1, 'AVAILABLE'),
('201', 3, 2, 'AVAILABLE'),  ('202', 3, 2, 'OCCUPIED'),    ('203', 3, 2, 'AVAILABLE'),  ('204', 3, 2, 'MAINTENANCE'),
('205', 4, 2, 'AVAILABLE'),  ('206', 4, 2, 'AVAILABLE'),   ('207', 4, 2, 'OCCUPIED'),   ('208', 4, 2, 'AVAILABLE'),
('301', 5, 3, 'AVAILABLE'),  ('302', 5, 3, 'OCCUPIED'),    ('303', 5, 3, 'AVAILABLE'),  ('304', 5, 3, 'MAINTENANCE'),
('305', 6, 3, 'AVAILABLE'),  ('306', 6, 3, 'AVAILABLE'),   ('307', 6, 3, 'OCCUPIED'),   ('308', 6, 3, 'AVAILABLE'),
('401', 7, 4, 'AVAILABLE'),  ('402', 7, 4, 'OCCUPIED'),    ('403', 7, 4, 'AVAILABLE'),  ('404', 7, 4, 'MAINTENANCE'),
('405', 8, 4, 'AVAILABLE'),  ('406', 8, 4, 'AVAILABLE'),   ('407', 8, 4, 'OCCUPIED'),   ('408', 8, 4, 'AVAILABLE'),
('501', 9, 5, 'AVAILABLE'),  ('502', 9, 5, 'OCCUPIED'),    ('503', 9, 5, 'AVAILABLE'),  ('504', 9, 5, 'MAINTENANCE'),
('505', 10, 5, 'AVAILABLE'), ('506', 10, 5, 'AVAILABLE'),  ('507', 10, 5, 'OCCUPIED'),  ('508', 10, 5, 'AVAILABLE');

-- ← Đổi toàn bộ tiếng Việt → Enum values
INSERT INTO bookings (customer_id, check_in_date, check_out_date, status) VALUES
(1,  '2024-05-01', '2024-05-03', 'CHECKED_OUT'), (2,  '2024-05-05', '2024-05-07', 'CHECKED_OUT'),
(3,  '2024-05-10', '2024-05-12', 'CHECKED_OUT'), (4,  '2024-05-15', '2024-05-20', 'CANCELLED'),
(5,  '2024-05-20', '2024-05-22', 'CHECKED_OUT'), (6,  '2024-06-01', '2024-06-05', 'CHECKED_OUT'),
(7,  '2024-06-10', '2024-06-11', 'CANCELLED'),   (8,  '2024-06-15', '2024-06-18', 'CHECKED_OUT'),
(9,  '2024-06-20', '2024-06-25', 'CHECKED_OUT'), (10, '2024-07-01', '2024-07-03', 'CHECKED_OUT'),
(11, '2024-07-05', '2024-07-10', 'CHECKED_OUT'), (12, '2024-07-15', '2024-07-16', 'CANCELLED'),
(13, '2024-08-01', '2024-08-05', 'CHECKED_OUT'), (14, '2024-08-10', '2024-08-12', 'CHECKED_OUT'),
(15, '2024-08-15', '2024-08-20', 'CHECKED_OUT'), (16, '2024-09-01', '2024-09-02', 'CHECKED_OUT'),
(17, '2024-09-10', '2024-09-15', 'CHECKED_OUT'), (18, '2024-09-20', '2024-09-22', 'CANCELLED'),
(19, '2024-10-01', '2024-10-05', 'CHECKED_OUT'), (20, '2024-10-10', '2024-10-12', 'CHECKED_OUT'),
(21, '2024-11-01', '2024-11-03', 'CHECKED_OUT'), (22, '2024-11-05', '2024-11-10', 'CHECKED_OUT'),
(23, '2024-11-15', '2024-11-20', 'CANCELLED'),   (24, '2024-12-01', '2024-12-05', 'CHECKED_OUT'),
(25, '2024-12-10', '2024-12-15', 'CHECKED_OUT'), (26, '2024-12-20', '2024-12-25', 'CHECKED_OUT'),
(27, '2025-01-01', '2025-01-05', 'CHECKED_OUT'), (28, '2025-01-10', '2025-01-12', 'CHECKED_OUT'),
(29, '2025-01-15', '2025-01-20', 'CANCELLED'),   (30, '2025-02-01', '2025-02-05', 'CHECKED_OUT'),
(1,  '2026-06-01', '2026-06-10', 'CHECKED_IN'),  -- booking 31 → phòng 102
(2,  '2026-06-02', '2026-06-08', 'CHECKED_IN'),  -- booking 32 → phòng 107
(3,  '2026-06-03', '2026-06-09', 'CHECKED_IN'),  -- booking 33 → phòng 202
(4,  '2026-06-01', '2026-06-07', 'CHECKED_IN'),  -- booking 34 → phòng 207
(5,  '2026-06-04', '2026-06-11', 'CHECKED_IN'),  -- booking 35 → phòng 302
(6,  '2026-06-02', '2026-06-06', 'CHECKED_IN'),  -- booking 36 → phòng 307
(7,  '2026-06-05', '2026-06-12', 'CHECKED_IN'),  -- booking 37 → phòng 402
(8,  '2026-06-03', '2026-06-08', 'CHECKED_IN'),  -- booking 38 → phòng 407
(9,  '2026-06-01', '2026-06-09', 'CHECKED_IN'),  -- booking 39 → phòng 502
(10, '2026-06-04', '2026-06-10', 'CHECKED_IN');  -- booking 40 → phòng 507

INSERT INTO booking_rooms (booking_id, room_id, price) VALUES
(1,1,600000),  (2,2,600000),   (3,3,600000),   (4,4,600000),
(5,5,750000),  (6,6,750000),   (7,7,750000),   (8,8,750000),
(9,9,1100000), (10,10,1100000),(11,11,1100000),(12,12,1100000),
(13,13,1300000),(14,14,1300000),(15,15,1300000),(16,16,1300000),
(17,17,2800000),(18,18,2800000),(19,19,2800000),(20,20,2800000),
(21,21,1700000),(22,22,1700000),(23,23,1700000),(24,24,1700000),
(25,25,850000), (26,26,850000), (27,27,850000), (28,28,850000),
(29,29,7000000),(30,30,7000000),(31, 2,  600000),   -- booking 31 → phòng 102 (Standard City View)
(32, 7,  750000),   -- booking 32 → phòng 107 (Standard Ocean View)
(33, 10, 1100000),  -- booking 33 → phòng 202 (Deluxe City View)
(34, 15, 1300000),  -- booking 34 → phòng 207 (Deluxe Ocean View)
(35, 18, 2800000),  -- booking 35 → phòng 302 (Suite Ocean Front)
(36, 23, 1700000),  -- booking 36 → phòng 307 (Family Garden)
(37, 26, 850000),   -- booking 37 → phòng 402 (Couple Romance)
(38, 31, 7000000),  -- booking 38 → phòng 407 (Villa 2 Bedrooms)
(39, 34, 1600000),  -- booking 39 → phòng 502 (Bungalow Ocean)
(40, 39, 15000000); -- booking 40 → phòng 507 (Presidential Suite)

INSERT INTO booking_services (booking_id, service_id, quantity) VALUES
(1,1,2),(2,5,1),(3,10,4),(4,3,2),(5,15,1),(6,20,2),(7,25,1),(8,30,1),(9,35,1),(10,40,1),
(11,2,1),(12,7,2),(13,12,3),(14,17,5),(15,22,2),(16,27,1),(17,32,4),(18,37,1),(19,4,1),(20,9,2),
(21,14,1),(22,19,2),(23,24,1),(24,29,3),(25,34,2),(26,39,1),(27,6,2),(28,11,4),(29,16,1),(30,21,2),
(31,26,1),(32,31,1),(33,36,1),(34,8,2),(35,13,1),(36,18,4),(37,23,2),(38,28,1),(39,33,2),(40,38,1);

-- ← Đổi payment_status tiếng Việt → Enum values: PAID | PENDING | FAILED
INSERT INTO payments (booking_id, amount, payment_method, payment_date, payment_status) VALUES
(1,  1500000,  'CARD', '2024-05-03', 'PAID'),
(2,  2000000,  'CASH', '2024-05-07', 'PAID'),
(3,  1200000,  'CARD', '2024-05-12', 'PAID'),
(4,  500000,   'CARD', NULL,         'FAILED'),
(5,  3000000,  'CASH', '2024-05-22', 'PAID'),
(6,  4500000,  'CARD', '2024-06-05', 'PAID'),
(7,  0,        'CASH', NULL,         'FAILED'),
(8,  8000000,  'CARD', '2024-06-18', 'PAID'),
(9,  10000000, 'CARD', '2024-06-25', 'PAID'),
(10, 3500000,  'CASH', '2024-07-03', 'PAID'),
(11, 11000000, 'CARD', '2024-07-10', 'PAID'),
(12, 1000000,  'CARD', NULL,         'FAILED'),
(13, 3500000,  'CASH', '2024-08-05', 'PAID'),
(14, 3200000,  'CARD', '2024-08-12', 'PAID'),
(15, 75000000, 'CARD', '2024-08-20', 'PAID'),
(16, 4500000,  'CASH', '2024-09-02', 'PAID'),
(17, 36000000, 'CARD', '2024-09-15', 'PAID'),
(18, 0,        'CASH', NULL,         'FAILED'),
(19, 50000000, 'CARD', '2024-10-05', 'PAID'),
(20, 2500000,  'CASH', '2024-10-12', 'PAID'),
(21, 3500000,  'CARD', '2024-11-03', 'PAID'),
(22, 2000000,  'CASH', '2024-11-10', 'PAID'),
(23, 0,        'CARD', NULL,         'FAILED'),
(24, 9000000,  'CARD', '2024-12-05', 'PAID'),
(25, 4500000,  'CASH', '2024-12-15', 'PAID'),
(26, 6000000,  'CARD', '2024-12-25', 'PAID'),
(27, 5800000,  'CARD', '2025-01-05', 'PAID'),
(28, 16000000, 'CASH', '2025-01-12', 'PAID'),
(29, 0,        'CARD', NULL,         'FAILED'),
(30, 7500000,  'CASH', '2025-02-05', 'PAID'),
(31, 5400000,   'CARD', NULL, 'PENDING'),  -- 9 đêm × 600000
(32, 4500000,   'CASH', NULL, 'PENDING'),  -- 6 đêm × 750000
(33, 6600000,   'CARD', NULL, 'PENDING'),  -- 6 đêm × 1100000
(34, 7800000,   'CARD', NULL, 'PENDING'),  -- 6 đêm × 1300000
(35, 19600000,  'CASH', NULL, 'PENDING'),  -- 7 đêm × 2800000
(36, 6800000,   'QR',   NULL, 'PENDING'),  -- 4 đêm × 1700000
(37, 5950000,   'CARD', NULL, 'PENDING'),  -- 7 đêm × 850000
(38, 35000000,  'CASH', NULL, 'PENDING'),  -- 5 đêm × 7000000
(39, 12800000,  'CARD', NULL, 'PENDING'),  -- 8 đêm × 1600000
(40, 90000000,  'CARD', NULL, 'PENDING');  -- 6 đêm × 15000000

-- Tài khoản admin mặc định (password: Admin@123 đã BCrypt)
INSERT INTO users (username, password, role, employee_id) VALUES
('admin', '$2a$12$KLxmtK2vnp4mrRig8WSuPefqAHM4ZSzTsbSbZLoVBEwre7GJbqa0K', 'ADMIN', NULL);

SELECT room_number, status FROM rooms LIMIT 5;

SELECT * FROM users;

DESCRIBE payments;


USE resort_management;
CREATE TABLE vip_tier_benefits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vip_tier VARCHAR(10) NOT NULL,
    service_id INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (service_id) REFERENCES services(id)
);

ALTER TABLE services ADD COLUMN category VARCHAR(50);
INSERT INTO services (service_name, price, category, created_at) VALUES
('Gym', 50000, 'GYM', NOW()),
('Ăn sáng buffet', 80000, 'BREAKFAST', NOW()),
('Vé hồ bơi', 60000, 'POOL', NOW());

SELECT id, service_name, category FROM services 
WHERE category IN ('GYM', 'BREAKFAST', 'POOL');

INSERT INTO vip_tier_benefits (vip_tier, service_id, created_at) VALUES
-- VIP_1: Gym + Breakfast
('VIP_1', 41, NOW()),
('VIP_1', 42, NOW()),
-- VIP_2: Gym + Breakfast + Pool
('VIP_2', 41, NOW()),
('VIP_2', 42, NOW()),
('VIP_2', 43, NOW()),
-- VIP_3
('VIP_3', 41, NOW()),
('VIP_3', 42, NOW()),
('VIP_3', 43, NOW()),
-- VIP_4
('VIP_4', 41, NOW()),
('VIP_4', 42, NOW()),
('VIP_4', 43, NOW()),
-- VIP_5
('VIP_5', 41, NOW()),
('VIP_5', 42, NOW()),
('VIP_5', 43, NOW());

ALTER TABLE persons 
ADD COLUMN total_spent DECIMAL(18,2) DEFAULT 0,
ADD COLUMN vip_tier VARCHAR(10) DEFAULT 'VIP_0';

ALTER TABLE booking_services 
ADD COLUMN price_override DECIMAL(18,2);

SET SQL_SAFE_UPDATES = 0;

UPDATE persons p
SET p.total_spent = (
    SELECT COALESCE(SUM(pay.amount), 0)
    FROM bookings b
    JOIN payments pay ON pay.booking_id = b.id
    WHERE b.customer_id = p.id
    AND pay.payment_status = 'PAID'
)
WHERE p.person_type = 'CUSTOMER';

UPDATE persons SET vip_tier = 
    CASE 
        WHEN total_spent >= 800000000 THEN 'VIP_5'
        WHEN total_spent >= 300000000 THEN 'VIP_4'
        WHEN total_spent >= 100000000 THEN 'VIP_3'
        WHEN total_spent >= 20000000  THEN 'VIP_2'
        WHEN total_spent >= 5000000   THEN 'VIP_1'
        ELSE 'VIP_0'
    END
WHERE person_type = 'CUSTOMER';

SET SQL_SAFE_UPDATES = 1;

SELECT id, full_name, total_spent, vip_tier 
FROM persons 
WHERE person_type = 'CUSTOMER'
ORDER BY total_spent DESC;

-- Chức năng giảm giá cho khách vip
ALTER TABLE payments 
ADD COLUMN discount_amount DECIMAL(18,2) DEFAULT 0;
