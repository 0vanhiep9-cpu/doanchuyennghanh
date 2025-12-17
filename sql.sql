SELECT `bangluong_chitiet`.`id`,
    `bangluong_chitiet`.`manhanvien`,
    `bangluong_chitiet`.`thangluong`,
    `bangluong_chitiet`.`cong_chuan`,
    `bangluong_chitiet`.`cong_thuc_te`,
    `bangluong_chitiet`.`nghi_co_luong`,
    `bangluong_chitiet`.`nghi_khong_luong`,
    `bangluong_chitiet`.`cong_ot`,
    `bangluong_chitiet`.`luong_co_ban_thuc_lanh`,
    `bangluong_chitiet`.`luong_ot`,
    `bangluong_chitiet`.`thuong_kpi`,
    `bangluong_chitiet`.`phu_cap_xang_xe`,
    `bangluong_chitiet`.`phu_cap_khac`,
    `bangluong_chitiet`.`tong_thu_nhap_gross`,
    `bangluong_chitiet`.`giam_tru_gia_canh`,
    `bangluong_chitiet`.`trich_bhxh`,
    `bangluong_chitiet`.`trich_bhyt`,
    `bangluong_chitiet`.`trich_bhtn`,
    `bangluong_chitiet`.`thu_nhap_chiu_thue`,
    `bangluong_chitiet`.`thue_tncn`,
    `bangluong_chitiet`.`tam_ung_khau_tru`,
    `bangluong_chitiet`.`tong_khau_tru`,
    `bangluong_chitiet`.`thuc_linh_net`
FROM `quanlynhansu`.`bangluong_chitiet`;
-- ======================================================================
-- FULL SQL SCRIPT (CREATE + INSERT) - Ready to run in PostgreSQL / pgAdmin4
-- Generates: tables, 34 nhân viên (from your provided list), luong master,
-- and bangluong_chitiet for 6 months (2025-03 -> 2025-08) for each nhân viên.
-- ======================================================================

-- ===========================
-- PHẦN 1: DROP TABLES (nếu có)
-- ===========================
DROP TABLE IF EXISTS bangluong_chitiet CASCADE;
DROP TABLE IF EXISTS nghiphep CASCADE;
DROP TABLE IF EXISTS quanlynhaplieu CASCADE;
DROP TABLE IF EXISTS taikhoan CASCADE;
DROP TABLE IF EXISTS khenthuongkyluat CASCADE;
DROP TABLE IF EXISTS chitietluong CASCADE;
DROP TABLE IF EXISTS luong CASCADE;
DROP TABLE IF EXISTS nhanvien CASCADE;
DROP TABLE IF EXISTS phongban CASCADE;
DROP TABLE IF EXISTS chucvu CASCADE;
DROP TABLE IF EXISTS hopdong CASCADE;

-- ===========================
-- PHẦN 2: TẠO CẤU TRÚC BẢNG
-- ===========================

CREATE TABLE phongban (
    maphongban VARCHAR(30) PRIMARY KEY,
    tenphongban VARCHAR(100) NOT NULL,
    diachi VARCHAR(200),
    sdt VARCHAR(15)
);

CREATE TABLE chucvu (
    machucvu VARCHAR(30) PRIMARY KEY,
    tenchucvu VARCHAR(100) NOT NULL,
    hesophucap FLOAT
);

CREATE TABLE hopdong (
    mahopdong VARCHAR(30) PRIMARY KEY,
    loaihopdong VARCHAR(50),
    ngaybatdau DATE,
    ngayketthuc DATE,
    ghichu VARCHAR(200)
);

CREATE TABLE nhanvien (
    manhanvien VARCHAR(30) PRIMARY KEY,
    hoten VARCHAR(100) NOT NULL,
    ngaysinh DATE,
    gioitinh VARCHAR(10),
    sdt VARCHAR(15),
    diachihientai VARCHAR(200),
    cccd VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    maphongban VARCHAR(30),
    machucvu VARCHAR(30),
    mahopdong VARCHAR(30),
    ngaynhap DATE,
    ngaynghi DATE,
    trangthai VARCHAR(50) DEFAULT 'Đang làm',
    trinhdototnghiep VARCHAR(50),
    thongtinanh VARCHAR(200),
    FOREIGN KEY (maphongban) REFERENCES phongban(maphongban),
    FOREIGN KEY (machucvu) REFERENCES chucvu(machucvu),
    FOREIGN KEY (mahopdong) REFERENCES hopdong(mahopdong)
);

-- Luong master (tóm tắt) — dùng để sinh dữ liệu chi tiết
CREATE TABLE luong (
    manhanvien VARCHAR(30) PRIMARY KEY,
    luong_hop_dong FLOAT DEFAULT 0,
    phucap_antrua FLOAT DEFAULT 0,
    phucap_xangxe FLOAT DEFAULT 0,
    phucap_khac FLOAT DEFAULT 0,
    so_nguoi_phu_thuoc INT DEFAULT 0,
    FOREIGN KEY (manhanvien) REFERENCES nhanvien(manhanvien) ON DELETE CASCADE
);

CREATE TABLE chitietluong (
    machitietluong SERIAL PRIMARY KEY,
    manhanvien VARCHAR(30) NOT NULL,
    thangluong DATE NOT NULL,
    tienthuong FLOAT DEFAULT 0,
    tienphat FLOAT DEFAULT 0,
    tongluong FLOAT NOT NULL,
    FOREIGN KEY (manhanvien) REFERENCES nhanvien(manhanvien) ON DELETE CASCADE
);

CREATE TABLE khenthuongkyluat (
    maktkl SERIAL PRIMARY KEY,
    manhanvien VARCHAR(30) NOT NULL,
    loai VARCHAR(20) NOT NULL,
    lydo VARCHAR(200),
    sotien FLOAT DEFAULT 0,
    ngaythuchien DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (manhanvien) REFERENCES nhanvien(manhanvien) ON DELETE CASCADE
);

CREATE TABLE taikhoan (
    tendangnhap VARCHAR(50) PRIMARY KEY,
    matkhau VARCHAR(100) NOT NULL,
    manhanvien VARCHAR(30),
    vaitro VARCHAR(20) NOT NULL,
    trangthai BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (manhanvien) REFERENCES nhanvien(manhanvien) ON DELETE CASCADE
);

CREATE TABLE quanlynhaplieu (
    malog SERIAL PRIMARY KEY,
    nguoinhap VARCHAR(50),
    bangdulieu VARCHAR(50) NOT NULL,
    thoigiannhap TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    giatricu TEXT,
    giatrimoi TEXT,
    FOREIGN KEY (nguoinhap) REFERENCES taikhoan(tendangnhap) ON DELETE SET NULL
);

-- Bảng chi tiết lương (cấu trúc bạn cung cấp)
CREATE TABLE bangluong_chitiet (
    id SERIAL PRIMARY KEY,
    manhanvien VARCHAR(30) NOT NULL,
    thangluong DATE NOT NULL,
    cong_chuan FLOAT DEFAULT 0,
    cong_thuc_te FLOAT DEFAULT 0,
    nghi_co_luong FLOAT DEFAULT 0,
    nghi_khong_luong FLOAT DEFAULT 0,
    cong_ot FLOAT DEFAULT 0,
    luong_co_ban_thuc_lanh FLOAT DEFAULT 0,
    luong_ot FLOAT DEFAULT 0,
    thuong_kpi FLOAT DEFAULT 0,
    phu_cap_xang_xe FLOAT DEFAULT 0,
    phu_cap_khac FLOAT DEFAULT 0,
    tong_thu_nhap_gross FLOAT DEFAULT 0,
    giam_tru_gia_canh FLOAT DEFAULT 0,
    trich_bhxh FLOAT DEFAULT 0,
    trich_bhyt FLOAT DEFAULT 0,
    trich_bhtn FLOAT DEFAULT 0,
    thu_nhap_chiu_thue FLOAT DEFAULT 0,
    thue_tncn FLOAT DEFAULT 0,
    tam_ung_khau_tru FLOAT DEFAULT 0,
    thuc_linh_net FLOAT DEFAULT 0,
    FOREIGN KEY (manhanvien) REFERENCES nhanvien(manhanvien) ON DELETE CASCADE,
    UNIQUE (manhanvien, thangluong)
);

CREATE TABLE nghiphep (
    manghiphep SERIAL PRIMARY KEY,
    manhanvien VARCHAR(30) REFERENCES nhanvien(manhanvien),
    ngaybatdau DATE NOT NULL,
    ngayketthuc DATE NOT NULL,
    lydo TEXT,            -- đổi từ lydonghi → lydo
    trangthai VARCHAR(50) DEFAULT 'Đang chờ'
);
-- ===========================
-- PHẦN 3: CHÈN DỮ LIỆU MẪU
-- ===========================

-- 3.1 Phòng ban
INSERT INTO phongban (maphongban, tenphongban, diachi, sdt) VALUES
('PB01', N'Ban Giám Đốc', NULL, NULL),
('PB02', N'Kinh Doanh', NULL, NULL),
('PB03', N'Marketing', NULL, NULL),
('PB04', N'Kế Toán', NULL, NULL),
('PB05', N'Nhân Sự', NULL, NULL),
('PB06', N'IT', NULL, NULL);

-- 3.2 Chức vụ
INSERT INTO chucvu (machucvu, tenchucvu, hesophucap) VALUES
('CV01', N'Tổng Giám Đốc', 5.0),
('CV02', N'Giám Đốc', 3.5),
('CV03', N'Trưởng Phòng', 2.0),
('CV04', N'Nhân Viên', 1.0),
('CV05', N'Giám Đốc Marketing', 3.5),
('CV06', N'Nhân Viên Marketing', 1.2),
('CV07', N'Nhân Viên IT', 1.3),
('CV08', N'Kế toán trưởng', 2.5),
('CV09', N'Kế toán thanh toán', 1.5),
('CV10', N'Kế toán công nợ', 1.5),
('CV11', N'Nhân viên kế toán', 1.2),
('CV12', N'Trưởng phòng nhân sự', 2.0),
('CV13', N'Nhân viên C&B', 1.4),
('CV14', N'Nhân viên tuyển dụng', 1.4),
('CV15', N'Nhân viên đào tạo', 1.4);

-- 3.3 Hợp đồng
INSERT INTO hopdong (mahopdong, loaihopdong, ngaybatdau, ngayketthuc) VALUES
('HD01', N'Chính thức', '2022-01-01', NULL),
('HD02', N'Học việc', '2024-01-01', '2024-03-01'),
('HD03', N'Thử việc', '2024-01-01', '2024-02-01');

-- 3.4 Nhân viên (34 bản ghi) -- **GIỮ NGUYÊN NHƯ BẠN ĐÃ CUNG CẤP**
INSERT INTO nhanvien (
    manhanvien, hoten, ngaysinh, gioitinh, sdt, diachihientai, cccd, email,
    maphongban, machucvu, mahopdong, ngaynhap, ngaynghi, trangthai, trinhdototnghiep, thongtinanh
) VALUES
('MS001', N'Nguyễn Văn Hải', '1981-04-11', N'Nam', '0991111111', N'Hà Nội', '001001000001', 'hai.nv@abc.com', 'PB01', 'CV01', 'HD01', '2022-03-31', NULL, N'Đang làm', N'Đại học', 'ms001.jpg'),
('MS002', N'Lê Văn Thọ', '1994-06-15', N'Nam', '0991111112', N'Hồ Chí Minh', '001001000002', 'tho.lv@abc.com', 'PB02', 'CV02', 'HD01', '2023-01-05', '2024-05-16', N'Đã nghỉ việc', N'Đại học', 'ms002.jpg'),
('MS003', N'Trần Minh Hạnh', '1996-11-09', N'Nữ', '0991111113', N'Thanh Hoá', '001001000003', 'hanh.tm@abc.com', 'PB02', 'CV03', 'HD02', '2022-12-16', NULL, N'Đang làm', N'Cao đẳng', 'ms003.jpg'),
('MS004', N'Ngô Văn Lâm', '1996-09-03', N'Nam', '0991111114', N'Hoà Bình', '001001000004', 'lam.nv@abc.com', 'PB02', 'CV03', 'HD02', '2023-10-20', NULL, N'Đang làm', N'Đại học', 'ms004.jpg'),
('MS005', N'Dương Văn Tuấn', '1995-05-27', N'Nam', '0991111115', N'Kiên Giang', '001001000005', 'tuan.dv@abc.com', 'PB02', 'CV03', 'HD03', '2023-07-06', '2023-12-14', N'Đã nghỉ việc', N'THPT', 'ms005.jpg'),
('MS006', N'Nguyễn Thị Trang', '1990-11-25', N'Nữ', '0991111116', N'Vũng Tàu', '001001000006', 'trang.nt@abc.com', 'PB02', 'CV04', 'HD03', '2023-03-17', NULL, N'Đang làm', N'Đại học', 'ms006.jpg'),
('MS007', N'Trần Thị Lan Anh', '1998-09-03', N'Nữ', '0991111117', N'Nghệ An', '001001000007', 'lananh.tt@abc.com', 'PB02', 'CV04', 'HD01', '2023-05-11', '2024-02-08', N'Nghỉ thai sản', N'Cao đẳng', 'ms007.jpg'),
('MS008', N'Nguyễn Thị Nhung', '1988-11-02', N'Nam', '0991111118', N'Hà Tĩnh', '001001000008', 'nhung.nt@abc.com', 'PB02', 'CV04', 'HD01', '2023-11-10', NULL, N'Đang làm', N'THPT', 'ms008.jpg'),
('MS009', N'Nguyễn Viết Minh', '1995-07-25', N'Nam', '0991111119', N'Hà Nội', '001001000009', 'minh.nv@abc.com', 'PB02', 'CV04', 'HD01', '2024-02-23', '2024-03-08', N'Đã nghỉ việc', N'THPT', 'ms009.jpg'),
('MS010', N'Phạm Thị Nhung', '1995-01-10', N'Nữ', '0991111120', N'Hải Phòng', '001001000010', 'nhung.pt@abc.com', 'PB04', 'CV08', 'HD01', '2023-08-15', NULL, N'Đang làm', N'Đại học', 'ms010.jpg'),
('MS011', N'Đinh Văn Linh', '1998-03-20', N'Nam', '0991111121', N'Quảng Ninh', '001001000011', 'linh.dv@abc.com', 'PB05', 'CV12', 'HD01', '2023-01-20', NULL, N'Đang làm', N'Đại học', 'ms011.jpg'),
('MS012', N'Phạm Hà Trang', '1999-05-25', N'Nữ', '0991111122', N'Hà Nội', '001001000012', 'trang.ph@abc.com', 'PB05', 'CV13', 'HD02', '2024-04-10', NULL, N'Đang làm', N'Cao đẳng', 'ms012.jpg'),
('MS013', N'Trần Gia Khải', '1990-11-12', N'Nam', '0991111123', N'Đà Nẵng', '001001000013', 'khai.tg@abc.com', 'PB02', 'CV02', 'HD01', '2021-06-01', NULL, N'Đang làm', N'Đại học', 'ms013.jpg'),
('MS014', N'Võ Văn Kiệt', '1993-02-28', N'Nam', '0991111124', 'Cần Thơ', '001001000014', 'kiet.vv@abc.com', 'PB02', 'CV03', 'HD01', '2022-08-01', NULL, N'Đang làm', N'Đại học', 'ms014.jpg'),
('MS015', N'Nguyễn Văn Toàn', '1982-04-21', N'Nam', '0991111125', N'Cần Thơ', '001001000015', 'toan.nv_old@abc.com', 'PB03', 'CV06', 'HD01', '2023-10-10', NULL, N'Đang làm', N'Đại học', 'ms015.jpg'),
('MS016', N'Lê Mỹ Tâm', '1983-10-29', N'Nữ', '0991111126', 'Bình Dương', '001001000016', 'tam.lm_old@abc.com', 'PB03', 'CV06', 'HD01', '2024-05-23', '2024-07-05', N'Đã nghỉ việc', N'Cao đẳng', 'ms016.jpg'),
('MS017', N'Trần Gia Khải', '1998-04-27', N'Nam', '0992221117', N'Hà Nội', '001001000017', 'khai.tg2@abc.com', 'PB02', 'CV04', 'HD01', '2024-06-06', NULL, N'Đang làm', N'Đại học', 'ms017.jpg'),
('MS018', N'Võ Văn Kiệt', '1998-01-16', N'Nam', '0992221118', N'TP Hồ Chí Minh', '001001000018', 'kiet.vv2@abc.com', 'PB02', 'CV04', 'HD01', '2024-06-06', NULL, N'Đang làm', N'Cao đẳng', 'ms018.jpg'),
('MS019', N'Lê Văn Hải', '1991-12-01', N'Nam', '0992221119', N'Đà Nẵng', '001001000019', 'hai.lv2@abc.com', 'PB02', 'CV04', 'HD01', '2024-05-31', NULL, N'Đang làm', N'Đại học', 'ms019.jpg'),
('MS020', N'Lê Minh Thọ', '1989-12-04', N'Nam', '0992221120', N'Hải Phòng', '001001000020', 'tho.lm2@abc.com', 'PB03', 'CV05', 'HD01', '2023-10-06', NULL, N'Đang làm', N'THPT', 'ms020.jpg'),
('MS021', N'Nguyễn Văn Toàn', '1982-04-21', N'Nam', '0992221121', N'Cần Thơ', '001001000021', 'toan.nv2@abc.com', 'PB03', 'CV06', 'HD01', '2023-10-10', NULL, N'Đang làm', N'Đại học', 'ms021.jpg'),
('MS022', N'Lê Mỹ Tâm', '1983-10-29', N'Nữ', '0992221122', 'Bình Dương', '001001000022', 'tam.lm2@abc.com', 'PB03', 'CV06', 'HD01', '2024-05-23', '2024-07-05', N'Đã nghỉ việc', N'Cao đẳng', 'ms022.jpg'),
('MS023', N'Trần Văn Linh', '1998-06-26', N'Nam', '0992221123', N'Vũng Tàu', '001001000023', 'linh.tv@abc.com', 'PB03', 'CV07', 'HD01', '2024-10-24', NULL, N'Đang làm', N'Cao đẳng', 'ms023.jpg'),
('MS024', N'Nguyễn Thị Hà Anh', '1992-05-04', N'Nữ', '0992221124', N'Thái Nguyên', '001001000024', 'haanh.nt@abc.com', 'PB03', 'CV07', 'HD01', '2024-02-16', NULL, N'Đang làm', N'THPT', 'ms024.jpg'),
('MS025', N'Ngô Hải Hòa', '1989-09-13', N'Nữ', '0992221125', N'Hà Tĩnh', '001001000025', 'hoa.nh@abc.com', 'PB05', 'CV12', 'HD01', '2023-11-17', NULL, N'Đang làm', N'Đại học', 'ms025.jpg'),
('MS026', N'Nguyễn Văn Tuấn', '1995-12-05', N'Nam', '0992221126', N'Phú Thọ', '001001000026', 'tuan.nv@abc.com', 'PB05', 'CV13', 'HD01', '2023-08-25', NULL, N'Đang làm', N'Cao đẳng', 'ms026.jpg'),
('MS027', N'Lê Minh Long', '1995-11-07', N'Nam', '0992221127', N'Thanh Hoá', '001001000027', 'long.lm@abc.com', 'PB05', 'CV14', 'HD01', '2023-08-08', NULL, N'Đang làm', N'Cao đẳng', 'ms027.jpg'),
('MS028', N'Trần Lê Bảo Trân', '1991-05-04', N'Nữ', '0992221128', N'Bến Tre', '001001000028', 'tran.lb@abc.com', 'PB05', 'CV15', 'HD01', '2023-12-08', NULL, N'Đang làm', N'Đại học', 'ms028.jpg'),
('MS029', N'Nguyễn Thị Mai Trang', '2000-06-27', N'Nữ', '0992221129', N'Lạng Sơn', '001001000029', 'trang.ntm@abc.com', 'PB04', 'CV08', 'HD01', '2023-09-09', NULL, N'Đang làm', N'Đại học', 'ms029.jpg'),
('MS030', N'Lê Khải Phiếu', '1990-09-21', N'Nam', '0992221130', N'Gia Lai', '001001000030', 'phieu.lk@abc.com', 'PB04', 'CV09', 'HD01', '2023-09-15', NULL, N'Đang làm', N'Cao đẳng', 'ms030.jpg'),
('MS031', N'Trần Duy Nhật', '1984-12-22', N'Nam', '0992221131', N'Nghệ An', '001001000031', 'nhat.td@abc.com', 'PB04', 'CV10', 'HD01', '2023-09-21', NULL, N'Đang làm', N'THPT', 'ms031.jpg'),
('MS032', N'Hà Minh Trang', '1996-10-04', N'Nữ', '0992221132', N'Hà Nội', '001001000032', 'trang.hm@abc.com', 'PB04', 'CV11', 'HD01', '2023-09-23', '2024-05-11', N'Đã nghỉ việc', N'Cao đẳng', 'ms032.jpg'),
('MS033', N'Lê Thị Hà', '1988-10-05', N'Nữ', '0992221133', N'TP Hồ Chí Minh', '001001000033', 'ha.lt@abc.com', 'PB04', 'CV11', 'HD01', '2023-08-24', NULL, N'Đang làm', N'Cao đẳng', 'ms033.jpg'),
('MS034', N'Nguyễn Thị Hà', '1993-09-26', N'Nữ', '0992221134', N'Đà Nẵng', '001001000034', 'ha.nt@abc.com', 'PB04', 'CV11', 'HD01', '2023-03-23', NULL, N'Đang làm', N'Cao đẳng', 'ms034.jpg');

-- 3.5 Tài khoản mẫu
INSERT INTO taikhoan (tendangnhap, matkhau, manhanvien, vaitro, trangthai) VALUES
('admin_hr', '123456', 'MS001', 'Admin', TRUE),
('tphanh', '123456', 'MS003', 'QuanLy', TRUE),
('trang_nv', '123456', 'MS006', 'NhanVien', TRUE);

-- 3.6 Luong master: tạo bằng SELECT từ nhanvien (logic như bạn từng viết)
INSERT INTO luong (manhanvien, luong_hop_dong, phucap_antrua, phucap_xangxe, phucap_khac, so_nguoi_phu_thuoc)
SELECT
    manhanvien,
    CASE
        WHEN manhanvien = 'MS001' THEN 50000000
        WHEN manhanvien IN ('MS002','MS003','MS007','MS010','MS013') THEN 30000000
        WHEN manhanvien IN ('MS023','MS024') THEN 18000000
        WHEN machucvu IN ('CV02','CV03','CV05','CV08','CV12') THEN 30000000
        ELSE 15000000
    END AS luong_hop_dong,
    1500000 AS phucap_antrua,
    1000000 AS phucap_xangxe,
    CASE WHEN manhanvien = 'MS001' THEN 5000000 ELSE 0 END AS phucap_khac,
    CASE WHEN manhanvien IN ('MS001','MS002','MS010','MS023') THEN 2 ELSE 0 END AS so_nguoi_phu_thuoc
FROM nhanvien;

-- 3.7 Một vài bản ghi chitietluong mẫu (nếu bạn vẫn cần)
-- (Lưu ý: chính dữ liệu chính xác lương chi tiết sẽ được sinh ở phần bangluong_chitiet)
INSERT INTO chitietluong (manhanvien, thangluong, tienthuong, tienphat, tongluong)
VALUES ('MS001', '2025-08-01', 0, 0, 54302885);

-- 3.8 Dữ liệu Khen thưởng/Kỷ luật (một số bản ghi mẫu)
INSERT INTO khenthuongkyluat (manhanvien, loai, lydo, sotien, ngaythuchien) VALUES
('MS001', N'Khen thưởng', N'Hoàn thành xuất sắc quý 3', 15000000, '2024-10-01'),
('MS003', N'Khen thưởng', N'Đạt KPI tháng', 5000000, '2025-08-28'),
('MS004', N'Kỷ luật', N'Vi phạm quy tắc công ty', -1000000, '2025-09-05'),
('MS010', N'Khen thưởng', N'Sáng kiến cải tiến', 2000000, '2025-11-01'),
('MS013', N'Khen thưởng', N'Thành tích lâu năm', 5000000, '2024-06-01'),
('MS017', N'Kỷ luật', N'Đi làm muộn thường xuyên', -500000, '2025-11-15'),
('MS020', N'Khen thưởng', N'Hoàn thành dự án lớn', 8000000, '2024-12-10'),
('MS029', N'Khen thưởng', N'Kiểm toán thành công', 3000000, '2025-01-20'),
('MS033', N'Kỷ luật', N'Sai sót trong báo cáo', -1500000, '2025-07-25'),
('MS026', N'Khen thưởng', N'Đào tạo nhân viên mới tốt', 1000000, '2024-09-01');

-- 3.9 Dữ liệu Nghỉ phép (một số bản ghi mẫu)
INSERT INTO nghiphep (manhanvien, ngaybatdau, ngayketthuc, lydo, trangthai) VALUES
('MS003', '2025-12-24', '2025-12-26', N'Nghỉ phép năm', N'Đã duyệt'),
('MS006', '2025-11-20', '2025-11-20', N'Việc riêng', N'Đã duyệt'),
('MS010', '2025-12-01', '2025-12-03', N'Nghỉ bù', N'Đã duyệt'),
('MS014', '2025-11-25', '2025-11-28', N'Khám bệnh', N'Đã duyệt'),
('MS015', '2025-11-27', '2025-11-27', N'Việc riêng', N'Chờ duyệt'),
('MS020', '2025-10-05', '2025-10-10', N'Nghỉ phép năm', N'Đã duyệt'),
('MS025', '2025-11-21', '2025-11-22', N'Nghỉ bù', N'Chờ duyệt'),
('MS029', '2025-12-30', '2025-12-31', N'Nghỉ phép năm', N'Đã duyệt'),
('MS033', '2025-11-29', '2025-11-29', N'Việc riêng', N'Đã duyệt'),
('MS011', '2025-12-05', '2025-12-05', N'Việc riêng', N'Đã duyệt');

-- 3.10 Một số bản ghi log nhập liệu mẫu
INSERT INTO quanlynhaplieu (nguoinhap, bangdulieu, giatricu, giatrimoi) VALUES
('admin_hr', 'nhanvien', NULL, 'Import initial data'),
('tphanh', 'khenthuongkyluat', NULL, 'Insert sample rewards'),
('trang_nv', 'nghiphep', NULL, 'Insert sample leave');

-- ===========================
-- PHẦN 4: SINH bangluong_chitiet CHO 6 THÁNG (2025-03 -> 2025-08)
-- ---------------------------
-- Cách làm: tạo bảng tạm months rồi INSERT ... SELECT từ luong CROSS JOIN months
-- với công thức tính toán cho mỗi nhân viên / tháng.
-- ===========================

-- 4.1 Tạo bảng tạm months
DROP TABLE IF EXISTS _tmp_months;
CREATE TEMP TABLE _tmp_months (thang DATE);
INSERT INTO _tmp_months (thang) VALUES
('2025-03-01'), ('2025-04-01'), ('2025-05-01'), ('2025-06-01'), ('2025-07-01'), ('2025-08-01');

-- 4.2 Chèn vào bangluong_chitiet bằng SELECT (sinh 34*6 = 204 dòng)
-- ===========================
-- Chèn dữ liệu chi tiết lương cho 6 tháng với nghỉ/OT ngẫu nhiên
-- ===========================

INSERT INTO bangluong_chitiet (
    manhanvien, thangluong,
    cong_chuan, cong_thuc_te, nghi_co_luong, nghi_khong_luong, cong_ot,
    luong_co_ban_thuc_lanh, luong_ot, thuong_kpi, phu_cap_xang_xe, phu_cap_khac,
    tong_thu_nhap_gross, giam_tru_gia_canh,
    trich_bhxh, trich_bhyt, trich_bhtn,
    thu_nhap_chiu_thue, thue_tncn, tam_ung_khau_tru, thuc_linh_net
)
SELECT
    l.manhanvien,
    m.thang,

    -- cong_chuan cố định
    26 AS cong_chuan,

    -- cong_thuc_te: 24->26, small variation ngẫu nhiên
    26 - FLOOR(RANDOM() * 3) AS cong_thuc_te,

    -- nghi_co_luong: 0 hoặc 1 ngẫu nhiên với tỷ lệ 20%
    CASE WHEN RANDOM() < 0.2 THEN 1 ELSE 0 END AS nghi_co_luong,

    -- nghi_khong_luong: 0 hoặc 1 ngẫu nhiên với tỷ lệ 10%
    CASE WHEN RANDOM() < 0.1 THEN 1 ELSE 0 END AS nghi_khong_luong,

    -- cong_ot: 0->8 ngẫu nhiên với tỷ lệ 30% có OT
    CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END AS cong_ot,

    -- luong_co_ban_thuc_lanh
    ((l.luong_hop_dong / 26.0) * (26 - FLOOR(RANDOM() * 3))) AS luong_co_ban_thuc_lanh,

    -- luong_ot
    ((l.luong_hop_dong / 26.0 / 8.0) * 1.5 *
        CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END
    ) AS luong_ot,

    -- thuong_kpi: ví dụ một vài tháng có thưởng
    CASE WHEN RANDOM() < 0.2 THEN 2000000 ELSE 0 END AS thuong_kpi,

    -- phu cap từ bảng luong
    l.phucap_antrua AS phu_cap_xang_xe,
    l.phucap_xangxe AS phu_cap_khac,

    -- tong gross
    ((l.luong_hop_dong / 26.0) * (26 - FLOOR(RANDOM() * 3))
     + ((l.luong_hop_dong / 26.0 / 8.0) * 1.5 * 
        CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END)
     + CASE WHEN RANDOM() < 0.2 THEN 2000000 ELSE 0 END
     + l.phucap_antrua + l.phucap_xangxe + l.phucap_khac
    ) AS tong_thu_nhap_gross,

    -- giam_tru_gia_canh
    (11000000 + (l.so_nguoi_phu_thuoc * 4400000)) AS giam_tru_gia_canh,

    -- trich BH
    (l.luong_hop_dong * 0.08) AS trich_bhxh,
    (l.luong_hop_dong * 0.015) AS trich_bhyt,
    (l.luong_hop_dong * 0.01) AS trich_bhtn,

    -- thu_nhap_chiu_thue
    GREATEST(0,
        ((l.luong_hop_dong / 26.0) * (26 - FLOOR(RANDOM() * 3))
        + ((l.luong_hop_dong / 26.0 / 8.0) * 1.5 * 
            CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END)
        + CASE WHEN RANDOM() < 0.2 THEN 2000000 ELSE 0 END
        + l.phucap_antrua + l.phucap_xangxe + l.phucap_khac
        ) - (l.luong_hop_dong * 0.08 + l.luong_hop_dong * 0.015 + l.luong_hop_dong * 0.01)
        - (11000000 + (l.so_nguoi_phu_thuoc * 4400000))
    ) AS thu_nhap_chiu_thue,

    -- thue_tncn
    (GREATEST(0,
        ((l.luong_hop_dong / 26.0) * (26 - FLOOR(RANDOM() * 3))
        + ((l.luong_hop_dong / 26.0 / 8.0) * 1.5 * 
            CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END)
        + CASE WHEN RANDOM() < 0.2 THEN 2000000 ELSE 0 END
        + l.phucap_antrua + l.phucap_xangxe + l.phucap_khac
        ) - (l.luong_hop_dong * 0.08 + l.luong_hop_dong * 0.015 + l.luong_hop_dong * 0.01)
        - (11000000 + (l.so_nguoi_phu_thuoc * 4400000))
    ) * 0.05) AS thue_tncn,

    -- tam_ung_khau_tru
    CASE WHEN l.manhanvien='MS001' THEN 500000 ELSE 0 END AS tam_ung_khau_tru,

    -- thuc_linh_net
    (
        ((l.luong_hop_dong / 26.0) * (26 - FLOOR(RANDOM() * 3))
        + ((l.luong_hop_dong / 26.0 / 8.0) * 1.5 *
            CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END)
        + CASE WHEN RANDOM() < 0.2 THEN 2000000 ELSE 0 END
        + l.phucap_antrua + l.phucap_xangxe + l.phucap_khac
        ) - (l.luong_hop_dong * 0.08 + l.luong_hop_dong * 0.015 + l.luong_hop_dong * 0.01)
        - (GREATEST(0,
            ((l.luong_hop_dong / 26.0) * (26 - FLOOR(RANDOM() * 3))
            + ((l.luong_hop_dong / 26.0 / 8.0) * 1.5 *
                CASE WHEN RANDOM() < 0.3 THEN FLOOR(RANDOM() * 9) ELSE 0 END)
            + CASE WHEN RANDOM() < 0.2 THEN 2000000 ELSE 0 END
            + l.phucap_antrua + l.phucap_xangxe + l.phucap_khac
            ) - (l.luong_hop_dong * 0.08 + l.luong_hop_dong * 0.015 + l.luong_hop_dong * 0.01)
            - (11000000 + (l.so_nguoi_phu_thuoc * 4400000))
        ) * 0.05)
        - CASE WHEN l.manhanvien='MS001' THEN 500000 ELSE 0 END
    ) AS thuc_linh_net

FROM luong l
CROSS JOIN _tmp_months m
ORDER BY l.manhanvien, m.thang;


-- 4.3 (Tùy chọn) : Nếu muốn xem tạm một số dòng kiểm tra:
-- SELECT * FROM bangluong_chitiet WHERE manhanvien='MS001' ORDER BY thangluong;
-- SELECT COUNT(*) FROM bangluong_chitiet; -- should be 204 (34*6)

-- ======================================================================
-- KẾT THÚC: Script đã tạo tất cả bảng và dữ liệu cần thiết
-- Chạy xong: bạn có thể query các bảng: nhanvien, luong, bangluong_chitiet, nghiphep, khenthuongkyluat, ...
-- ======================================================================

-- Bổ sung cột tổng khấu trừ vào bảng chi tiết lương
ALTER TABLE bangluong_chitiet 
ADD COLUMN IF NOT EXISTS tong_khau_tru FLOAT DEFAULT 0;

-- Cập nhật giá trị cho cột này (nếu chưa có)
UPDATE bangluong_chitiet 
SET tong_khau_tru = trich_bhxh + trich_bhyt + trich_bhtn + thue_tncn + tam_ung_khau_tru;

-- 1. Tạo bảng Chấm Công
CREATE TABLE chamcong (
    machamcong SERIAL PRIMARY KEY,
    manhanvien VARCHAR(30) NOT NULL,
    ngay DATE NOT NULL,              -- Ngày chấm công
    gio_vao TIME,                    -- Giờ check-in
    gio_ra TIME,                     -- Giờ check-out
    phut_di_muon INT DEFAULT 0,      -- Số phút đi muộn (so với 8:00)
    trangthai VARCHAR(50) DEFAULT 'Đang làm việc', -- Đang làm, Đã về, Vắng, Nghỉ phép
    ghi_chu VARCHAR(200),
    
    FOREIGN KEY (manhanvien) REFERENCES nhanvien(manhanvien) ON DELETE CASCADE,
    UNIQUE (manhanvien, ngay) -- Một nhân viên chỉ có 1 dòng chấm công mỗi ngày
);

-- 2. Chèn dữ liệu mẫu cho tháng 11/2025 (Giả lập)
-- MS001: Đi làm đúng giờ
INSERT INTO chamcong (manhanvien, ngay, gio_vao, gio_ra, phut_di_muon, trangthai) 
VALUES ('MS001', '2025-11-22', '07:55:00', '17:00:00', 0, 'Đã về');

-- MS002: Đi muộn 15 phút (8:15 mới đến)
INSERT INTO chamcong (manhanvien, ngay, gio_vao, gio_ra, phut_di_muon, trangthai) 
VALUES ('MS002', '2025-11-22', '08:15:00', '17:30:00', 15, 'Đã về');

-- MS006: Nhân viên đang đăng nhập (Chưa check-out)
INSERT INTO chamcong (manhanvien, ngay, gio_vao, gio_ra, phut_di_muon, trangthai) 
VALUES ('MS006', '2025-11-22', '07:50:00', NULL, 0, 'Đang làm việc');


-- 1. Tạo bảng Tuyển Dụng
CREATE TABLE tuyendung (
    ma_job VARCHAR(30) PRIMARY KEY,         -- Mã số Job (J001...)
    vi_tri_cong_viec VARCHAR(200) NOT NULL, -- Vị trí tuyển dụng
    maphongban VARCHAR(30),                 -- Phòng ban cần tuyển
    nguoi_tuyen_dung VARCHAR(30),           -- Mã nhân viên phụ trách (MSxxx)
    
    so_luong_tuyen INT DEFAULT 1,           -- SL cần tuyển
    ngay_mo_don DATE,                       -- Ngày bắt đầu tuyển
    ngay_onboard_du_kien DATE,              -- Ngày dự kiến đi làm
    
    muc_luong_du_kien FLOAT DEFAULT 0,      -- Mức lương (Deal lương)
    trang_thai VARCHAR(50) DEFAULT 'Đang mở', -- Đang mở, Đã đóng, Tạm dừng, Đã huỷ
    
    mo_ta_cong_viec TEXT,                   -- JD
    
    FOREIGN KEY (maphongban) REFERENCES phongban(maphongban),
    FOREIGN KEY (nguoi_tuyen_dung) REFERENCES nhanvien(manhanvien)
);

-- 2. Chèn dữ liệu mẫu (Khớp với Excel của bạn)
INSERT INTO tuyendung (ma_job, maphongban, vi_tri_cong_viec, so_luong_tuyen, ngay_mo_don, nguoi_tuyen_dung, trang_thai, ngay_onboard_du_kien, muc_luong_du_kien) VALUES
('J001', 'PB04', N'Kiểm kê tài sản', 1, '2025-07-01', 'MS001', N'Đang mở', '2025-07-27', 30000000),
('J002', 'PB05', N'Chuyên viên Tuyển dụng', 2, '2025-07-05', 'MS010', N'Đang mở', '2025-08-01', 15000000),
('J003', 'PB01', N'Chuyên viên Phân tích Chiến lược', 2, '2025-07-01', 'MS001', N'Đang mở', '2025-07-25', 20000000),
('J004', 'PB04', N'Nhân viên Kế toán tổng hợp', 1, '2025-07-03', 'MS008', N'Đang mở', '2025-07-28', 10000000),
('J005', 'PB02', N'Chuyên viên Tài chính doanh nghiệp', 1, '2025-07-05', 'MS002', N'Đang mở', '2025-08-01', 8000000),
('J006', 'PB02', N'Quản lý Dự án Chiến lược', 1, '2025-07-07', 'MS003', N'Đã đóng', '2025-08-10', 15000000),
('J007', 'PB03', N'Chuyên viên Khảo sát & Phân tích', 2, '2025-07-09', 'MS013', N'Đang mở', '2025-08-15', 10000000),
('J008', 'PB02', N'Nhân viên Kế hoạch Tài chính', 1, '2025-07-11', 'MS004', N'Tạm dừng', '2025-08-18', 8000000),
('J012', 'PB02', N'Chuyên viên Phát triển Dự án', 2, '2025-07-19', 'MS019', N'Đã huỷ', '2025-08-29', 8000000);


-- 2. Tạo bảng Ứng Viên
CREATE TABLE ungvien (
    ma_ung_vien VARCHAR(30) PRIMARY KEY,    -- Mã ứng viên (UV001...)
    ho_ten VARCHAR(100) NOT NULL,
    ngay_sinh DATE,
    gioi_tinh VARCHAR(10),                  -- Nam/Nữ
    email VARCHAR(100),
    sdt VARCHAR(15),
    dia_chi VARCHAR(200) DEFAULT N'Tòa nhà Bitexco Financial Tower, số 2 Hải Triều, Bến Nghé, Quận 1, TP.HCM',
    
    ma_job VARCHAR(30),                     -- Ứng tuyển vào Job nào (Liên kết với bảng tuyendung)
    ngay_ung_tuyen DATE DEFAULT CURRENT_DATE,
    
    giai_doan VARCHAR(50) DEFAULT 'Sơ loại', -- Sơ loại, Phỏng vấn, Kiểm tra, Offer, Onboard
    trang_thai VARCHAR(50) DEFAULT 'Đang xử lý', -- Tuyển dụng, Không tuyển, Từ chối offer...
    ket_qua_pv VARCHAR(50),                 -- Đạt/Trượt
    ngay_pv DATE,                           -- Ngày phỏng vấn
    gio_pv TIME,                            -- Giờ phỏng vấn
    dia_diem_pv VARCHAR(200),               -- Link online hoặc địa chỉ
    
    FOREIGN KEY (ma_job) REFERENCES tuyendung(ma_job) ON DELETE SET NULL
);

-- 3. Chèn 10 Dữ liệu mẫu (TP.HCM, SĐT 09..., Email theo tên)
INSERT INTO ungvien (ma_ung_vien, ho_ten, ngay_sinh, gioi_tinh, email, sdt, ma_job, giai_doan, trang_thai, ngay_pv, gio_pv, dia_diem_pv) VALUES
('UV001', N'Nguyễn Thị Bích', '2000-06-30', N'Nữ', 'bichnt@gmail.com', '0901234567', 'J001', N'Phỏng vấn', N'Tuyển dụng', '2025-07-15', '09:00', N'Phòng họp 3, Tòa nhà Bitexco'),
('UV002', N'Lê Thị Thanh Huyền', '1997-03-23', N'Nữ', 'huyenltt@gmail.com', '0909876543', 'J002', N'Đánh giá CV', N'Không tuyển', NULL, NULL, NULL),
('UV003', N'Nguyễn Quốc Toàn', '1995-11-05', N'Nam', 'toannq@gmail.com', '0918273645', 'J003', N'Kiểm tra', N'Từ chối offer', '2025-07-16', '14:00', N'Online (Zoom)'),
('UV004', N'Phạm Thị Mai Anh', '1999-09-18', N'Nữ', 'anhptm@gmail.com', '0933445566', 'J003', N'Kiểm tra', N'Không tuyển', '2025-07-16', '15:00', N'Online (Zoom)'),
('UV005', N'Đỗ Minh Tuấn', '2001-02-28', N'Nam', 'tuandm@gmail.com', '0977889900', 'J004', N'Phỏng vấn', N'Tuyển dụng', '2025-07-17', '10:00', N'Phòng họp 2, Tòa nhà Bitexco'),
('UV006', N'Nguyễn Hữu Dũng', '1996-07-14', N'Nam', 'dungnh@gmail.com', '0966554433', 'J007', N'Mời Offer', N'Tuyển dụng', NULL, NULL, NULL),
('UV007', N'Trần Thị Kim Oanh', '2000-08-09', N'Nữ', 'oanhttk@gmail.com', '0922113344', 'J006', N'Phỏng vấn', N'Tuyển dụng', '2025-07-18', '09:30', N'Online (Google Meet)'), -- Sửa J009 -> J006
('UV008', N'Lê Hoàng Nam', '1998-01-11', N'Nam', 'namlh@gmail.com', '0944556677', 'J003', N'Từ chối', N'Không tuyển', NULL, NULL, NULL),
('UV009', N'Phạm Thanh Tùng', '1995-12-25', N'Nam', 'tungpt@gmail.com', '0911223388', 'J012', N'Phỏng vấn', N'Tuyển dụng', '2025-07-19', '13:30', N'Phòng họp 1, Tòa nhà Bitexco'),
('UV010', N'Trịnh Thị Thu Trang', '1997-04-03', N'Nữ', 'trangttt@gmail.com', '0905667788', 'J005', N'Đánh giá CV', N'Không tuyển', NULL, NULL, NULL); -- Sửa J011 -> J005




//////////////
-- ======================================================================
-- CẬP NHẬT DATABASE CHO TÍNH NĂNG CHUYỂN KHOẢN LƯƠNG
-- ======================================================================

-- 1. Thêm các cột thông tin ngân hàng vào bảng nhanvien
ALTER TABLE nhanvien 
ADD COLUMN IF NOT EXISTS ten_ngan_hang VARCHAR(100),
ADD COLUMN IF NOT EXISTS so_tai_khoan VARCHAR(50),
ADD COLUMN IF NOT EXISTS chu_tai_khoan VARCHAR(100),
ADD COLUMN IF NOT EXISTS chi_nhanh VARCHAR(200);

-- 2. Thêm các cột chuyển khoản vào bảng bangluong_chitiet
ALTER TABLE bangluong_chitiet 
ADD COLUMN IF NOT EXISTS phuong_thuc_tra_luong VARCHAR(20) DEFAULT 'Tiền mặt',
ADD COLUMN IF NOT EXISTS ngay_chuyen_khoan TIMESTAMP,
ADD COLUMN IF NOT EXISTS ma_giao_dich VARCHAR(50),
ADD COLUMN IF NOT EXISTS trang_thai_chuyen_khoan VARCHAR(20) DEFAULT 'Chưa chuyển',
ADD COLUMN IF NOT EXISTS ghi_chu_chuyen_khoan TEXT;

-- 3. Tạo bảng lịch sử chuyển khoản
CREATE TABLE IF NOT EXISTS lichsu_chuyenkhoan (
    ma_giao_dich VARCHAR(50) PRIMARY KEY,
    bang_luong_id INTEGER NOT NULL,
    
    so_tien_chuyen FLOAT NOT NULL,
    phi_chuyen_khoan FLOAT DEFAULT 0,
    so_tien_thuc_nhan FLOAT NOT NULL,
    
    ngay_tao_lenh TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ngay_thuc_hien TIMESTAMP,
    
    ngan_hang_nhan VARCHAR(100) NOT NULL,
    so_tk_nhan VARCHAR(50) NOT NULL,
    ten_tk_nhan VARCHAR(100) NOT NULL,
    
    trang_thai VARCHAR(20) DEFAULT 'Chờ xử lý',
    ma_tham_chieu_ngan_hang VARCHAR(100),
    ly_do_that_bai TEXT,
    nguoi_thuc_hien VARCHAR(50),
    
    FOREIGN KEY (bang_luong_id) REFERENCES bangluong_chitiet(id) ON DELETE CASCADE
);

-- 4. Thêm ràng buộc cho các trường choices
ALTER TABLE bangluong_chitiet 
ADD CONSTRAINT check_phuong_thuc_tra_luong 
CHECK (phuong_thuc_tra_luong IN ('Tiền mặt', 'Chuyển khoản'));

ALTER TABLE bangluong_chitiet 
ADD CONSTRAINT check_trang_thai_chuyen_khoan 
CHECK (trang_thai_chuyen_khoan IN ('Chưa chuyển', 'Đang xử lý', 'Thành công', 'Thất bại'));

ALTER TABLE lichsu_chuyenkhoan 
ADD CONSTRAINT check_trang_thai_lichsu 
CHECK (trang_thai IN ('Chờ xử lý', 'Đang xử lý', 'Thành công', 'Thất bại', 'Đã hủy'));

-- 5. Tạo index để tăng hiệu suất truy vấn
CREATE INDEX IF NOT EXISTS idx_bangluong_phuong_thuc ON bangluong_chitiet(phuong_thuc_tra_luong);
CREATE INDEX IF NOT EXISTS idx_bangluong_trang_thai_ck ON bangluong_chitiet(trang_thai_chuyen_khoan);
CREATE INDEX IF NOT EXISTS idx_lichsu_trang_thai ON lichsu_chuyenkhoan(trang_thai);
CREATE INDEX IF NOT EXISTS idx_lichsu_ngay_tao ON lichsu_chuyenkhoan(ngay_tao_lenh);

-- 6. Cập nhật dữ liệu mẫu thông tin ngân hàng cho một số nhân viên
UPDATE nhanvien SET 
    ten_ngan_hang = 'Vietcombank',
    so_tai_khoan = '1234567890',
    chu_tai_khoan = hoten,
    chi_nhanh = 'Chi nhánh Hà Nội'
WHERE manhanvien IN ('MS001', 'MS002', 'MS003', 'MS004', 'MS005');

UPDATE nhanvien SET 
    ten_ngan_hang = 'VietinBank',
    so_tai_khoan = '9876543210',
    chu_tai_khoan = hoten,
    chi_nhanh = 'Chi nhánh TP.HCM'
WHERE manhanvien IN ('MS006', 'MS007', 'MS008', 'MS009', 'MS010');

UPDATE nhanvien SET 
    ten_ngan_hang = 'BIDV',
    so_tai_khoan = '5555666677',
    chu_tai_khoan = hoten,
    chi_nhanh = 'Chi nhánh Đà Nẵng'
WHERE manhanvien IN ('MS011', 'MS012', 'MS013', 'MS014', 'MS015');

-- 7. Cập nhật phương thức trả lương cho bảng lương hiện có
UPDATE bangluong_chitiet SET 
    phuong_thuc_tra_luong = 'Chuyển khoản',
    trang_thai_chuyen_khoan = 'Chưa chuyển'
WHERE manhanvien IN (
    SELECT manhanvien 
    FROM nhanvien 
    WHERE ten_ngan_hang IS NOT NULL 
      AND so_tai_khoan IS NOT NULL
);

-- 8. Kiểm tra kết quả
SELECT 'Thông tin ngân hàng đã cập nhật:' AS message;
SELECT manhanvien, hoten, ten_ngan_hang, so_tai_khoan 
FROM nhanvien 
WHERE ten_ngan_hang IS NOT NULL 
ORDER BY manhanvien;

SELECT 'Bảng lương với phương thức chuyển khoản:' AS message;
SELECT COUNT(*) AS so_luong_chuyen_khoan
FROM bangluong_chitiet 
WHERE phuong_thuc_tra_luong = 'Chuyển khoản';

COMMIT;




///////////////

-- ======================================================================
-- CẬP NHẬT DATABASE CHO TÍNH NĂNG PHÊ DUYỆT TÀI KHOẢN
-- ======================================================================

-- 1. Thêm các cột mới vào bảng taikhoan
ALTER TABLE taikhoan 
ADD COLUMN IF NOT EXISTS trang_thai_duyet VARCHAR(20) DEFAULT 'Chờ duyệt',
ADD COLUMN IF NOT EXISTS ngay_tao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS ngay_duyet TIMESTAMP,
ADD COLUMN IF NOT EXISTS nguoi_duyet VARCHAR(50),
ADD COLUMN IF NOT EXISTS ly_do_tu_choi TEXT;

-- 2. Thêm ràng buộc cho trạng thái duyệt
ALTER TABLE taikhoan 
ADD CONSTRAINT check_trang_thai_duyet 
CHECK (trang_thai_duyet IN ('Chờ duyệt', 'Đã duyệt', 'Từ chối'));

-- 3. Cập nhật tất cả tài khoản hiện có thành "Đã duyệt" (để không ảnh hưởng đến tài khoản cũ)
UPDATE taikhoan 
SET trang_thai_duyet = 'Đã duyệt', 
    ngay_duyet = CURRENT_TIMESTAMP,
    nguoi_duyet = 'System'
WHERE trang_thai_duyet = 'Chờ duyệt';

-- 4. Tạo index để tăng hiệu suất truy vấn
CREATE INDEX IF NOT EXISTS idx_taikhoan_trang_thai_duyet ON taikhoan(trang_thai_duyet);
CREATE INDEX IF NOT EXISTS idx_taikhoan_ngay_tao ON taikhoan(ngay_tao);

-- 5. Kiểm tra kết quả
SELECT 'Cập nhật thành công!' as message;
SELECT trang_thai_duyet, COUNT(*) as so_luong 
FROM taikhoan 
GROUP BY trang_thai_duyet;

COMMIT;








///////////
-- Thêm dữ liệu mẫu cho hợp đồng
-- Chạy script này trong PostgreSQL để có dữ liệu test

-- Thêm các hợp đồng mẫu
INSERT INTO hopdong (mahopdong, loaihopdong, ngaybatdau, ngayketthuc, ghichu) VALUES
('HD001', 'Hợp đồng không thời hạn', '2023-01-01', NULL, 'Hợp đồng chính thức cho nhân viên cấp cao'),
('HD002', 'Hợp đồng có thời hạn', '2024-01-01', '2024-12-31', 'Hợp đồng 1 năm cho nhân viên mới'),
('HD003', 'Hợp đồng thử việc', '2024-10-01', '2024-12-01', 'Hợp đồng thử việc 2 tháng'),
('HD004', 'Hợp đồng thực tập', '2024-06-01', '2024-08-31', 'Hợp đồng thực tập sinh mùa hè'),
('HD005', 'Hợp đồng có thời hạn', '2023-06-01', '2024-05-31', 'Hợp đồng đã hết hạn - cần gia hạn'),
('HD006', 'Hợp đồng cộng tác viên', '2024-01-01', '2024-06-30', 'Hợp đồng cộng tác viên part-time'),
('HD007', 'Hợp đồng có thời hạn', '2024-03-01', '2025-02-28', 'Hợp đồng 1 năm cho phòng Marketing'),
('HD008', 'Hợp đồng thử việc', '2024-11-01', '2025-01-01', 'Hợp đồng thử việc cho vị trí Developer');

-- Cập nhật một số nhân viên để sử dụng hợp đồng mới
UPDATE nhanvien SET mahopdong = 'HD001' WHERE manhanvien IN ('MS001', 'MS002', 'MS003');
UPDATE nhanvien SET mahopdong = 'HD002' WHERE manhanvien IN ('MS004', 'MS005', 'MS006');
UPDATE nhanvien SET mahopdong = 'HD003' WHERE manhanvien IN ('MS007', 'MS008');
UPDATE nhanvien SET mahopdong = 'HD005' WHERE manhanvien IN ('MS009', 'MS010');
UPDATE nhanvien SET mahopdong = 'HD007' WHERE manhanvien IN ('MS011', 'MS012');

-- Kiểm tra dữ liệu
SELECT 
    hd.mahopdong,
    hd.loaihopdong,
    hd.ngaybatdau,
    hd.ngayketthuc,
    COUNT(nv.manhanvien) as so_nhan_vien,
    CASE 
        WHEN hd.ngayketthuc IS NULL THEN 'Không thời hạn'
        WHEN hd.ngayketthuc < CURRENT_DATE THEN 'Hết hạn'
        ELSE 'Còn hiệu lực'
    END as trang_thai
FROM hopdong hd
LEFT JOIN nhanvien nv ON hd.mahopdong = nv.mahopdong
GROUP BY hd.mahopdong, hd.loaihopdong, hd.ngaybatdau, hd.ngayketthuc
ORDER BY hd.mahopdong;