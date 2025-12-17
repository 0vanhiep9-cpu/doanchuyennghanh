# Thư mục lưu trữ ảnh đại diện nhân viên

## Cách sử dụng:

### 1. Upload ảnh qua giao diện web:
- Vào "Danh Sách Nhân Sự" → Chọn nhân viên → "Chỉnh sửa"
- Tại mục "Ảnh Đại Diện", chọn file ảnh từ máy tính
- Nhấn "Lưu Thay Đổi"

### 2. Yêu cầu ảnh:
- **Định dạng:** JPG, PNG, GIF
- **Kích thước:** Tối đa 5MB
- **Khuyến nghị:** Ảnh vuông (1:1) để hiển thị đẹp nhất

### 3. Ảnh sẽ được lưu tại:
- **Đường dẫn:** `/media/avatars/`
- **URL truy cập:** `http://localhost:8000/media/avatars/ten_file.jpg`

### 4. Hiển thị ảnh:
- **Hồ sơ cá nhân:** Ảnh lớn 192x256px
- **Header:** Ảnh nhỏ 36x36px (tròn)
- **Danh sách:** Ảnh thumbnail

### 5. Lưu ý:
- Ảnh sẽ được tự động đổi tên khi upload để tránh trùng lặp
- Ảnh cũ sẽ được giữ lại trong thư mục (không tự động xóa)
- Nếu không có ảnh, hệ thống sẽ hiển thị icon mặc định

## Cấu trúc thư mục:
```
media/
└── avatars/
    ├── avatar_MS001_2024.jpg
    ├── avatar_MS002_2024.png
    └── ...
```