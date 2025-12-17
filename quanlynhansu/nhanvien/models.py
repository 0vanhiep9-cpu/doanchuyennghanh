from django.db import models
from django.db.models.deletion import SET_NULL, CASCADE

# --- CÁC MODEL DANH MỤC & HỒ SƠ (GIỮ NGUYÊN) ---
class PhongBan(models.Model):
    maphongban = models.CharField(max_length=30, primary_key=True)
    tenphongban = models.CharField(max_length=100)
    diachi = models.CharField(max_length=200, blank=True, null=True)
    sdt = models.CharField(max_length=15, blank=True, null=True)
    class Meta:
        db_table = 'phongban'
    def __str__(self): return self.tenphongban

class ChucVu(models.Model):
    machucvu = models.CharField(max_length=30, primary_key=True)
    tenchucvu = models.CharField(max_length=100)
    hesophucap = models.FloatField(blank=True, null=True)
    class Meta:
        db_table = 'chucvu'
    def __str__(self): return self.tenchucvu

class HopDong(models.Model):
    mahopdong = models.CharField(max_length=30, primary_key=True)
    loaihopdong = models.CharField(max_length=50, blank=True, null=True)
    ngaybatdau = models.DateField()
    ngayketthuc = models.DateField(blank=True, null=True)
    ghichu = models.CharField(blank=True, max_length=200, null=True)
    class Meta:
        db_table = 'hopdong'

class NhanVien(models.Model):
    manhanvien = models.CharField(max_length=30, primary_key=True)
    hoten = models.CharField(max_length=100)
    ngaysinh = models.DateField(blank=True, null=True)
    gioitinh = models.CharField(blank=True, max_length=10, null=True)
    sdt = models.CharField(blank=True, max_length=15, null=True)
    diachihientai = models.CharField(blank=True, max_length=200, null=True)
    cccd = models.CharField(blank=True, max_length=50, null=True, unique=True)
    email = models.EmailField(max_length=100, unique=True)

    # Thông tin ngân hàng (mới thêm)
    ten_ngan_hang = models.CharField(max_length=100, blank=True, null=True)
    so_tai_khoan = models.CharField(max_length=50, blank=True, null=True)
    chu_tai_khoan = models.CharField(max_length=100, blank=True, null=True)
    chi_nhanh = models.CharField(max_length=200, blank=True, null=True)

    maphongban = models.ForeignKey(PhongBan, on_delete=SET_NULL, db_column='maphongban', blank=True, null=True)
    machucvu = models.ForeignKey(ChucVu, on_delete=SET_NULL, db_column='machucvu', blank=True, null=True)
    mahopdong = models.ForeignKey(HopDong, on_delete=SET_NULL, db_column='mahopdong', blank=True, null=True)

    ngaynhap = models.DateField(blank=True, null=True)
    ngaynghi = models.DateField(blank=True, null=True)
    trangthai = models.CharField(default='Đang làm', max_length=50)
    trinhdototnghiep = models.CharField(blank=True, max_length=50, null=True)
    thongtinanh = models.CharField(blank=True, max_length=200, null=True, verbose_name='Ảnh đại diện')

    class Meta:
        db_table = 'nhanvien'

    @property
    def vaitro(self):
        try: return self.taikhoan.vaitro
        except: return 'Guest'

class TaiKhoan(models.Model):
    tendangnhap = models.CharField(max_length=50, primary_key=True)
    matkhau = models.CharField(max_length=100) 
    manhanvien = models.OneToOneField(NhanVien, on_delete=CASCADE, db_column='manhanvien', blank=True, null=True, related_name='taikhoan')
    vaitro = models.CharField(max_length=20)
    trangthai = models.BooleanField(default=True)
    
    # Thêm trạng thái phê duyệt
    trang_thai_duyet = models.CharField(max_length=20, default='Chờ duyệt', choices=[
        ('Chờ duyệt', 'Chờ duyệt'),
        ('Đã duyệt', 'Đã duyệt'),
        ('Từ chối', 'Từ chối')
    ])
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_duyet = models.DateTimeField(blank=True, null=True)
    nguoi_duyet = models.CharField(max_length=50, blank=True, null=True)
    ly_do_tu_choi = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'taikhoan'

# --- MODEL LƯƠNG MASTER ---

class Luong(models.Model):
    manhanvien = models.OneToOneField('NhanVien', on_delete=CASCADE, db_column='manhanvien', primary_key=True)
    luong_hop_dong = models.FloatField(default=0) 
    phucap_antrua = models.FloatField(default=0)
    phucap_xangxe = models.FloatField(default=0)
    phucap_khac = models.FloatField(default=0)
    so_nguoi_phu_thuoc = models.IntegerField(default=0)
    hesoluong = models.FloatField(default=1.0)

    class Meta:
        db_table = 'luong'

# --- MODEL CHI TIẾT BẢNG LƯƠNG ---

class ChiTietBangLuong(models.Model):
    manhanvien = models.ForeignKey('NhanVien', on_delete=CASCADE, db_column='manhanvien')
    thang_luong = models.DateField(db_column='thangluong') 

    cong_chuan = models.FloatField(default=0)
    cong_thuc_te = models.FloatField(default=0)
    nghi_co_luong = models.FloatField(default=0) 
    nghi_khong_luong = models.FloatField(default=0)
    cong_ot = models.FloatField(default=0)

    luong_co_ban_thuc_lanh = models.FloatField(default=0)
    luong_ot = models.FloatField(default=0)
    thuong_kpi = models.FloatField(default=0)
    phu_cap_xang_xe = models.FloatField(default=0)
    phu_cap_khac = models.FloatField(default=0)
    tong_thu_nhap_gross = models.FloatField(default=0)

    giam_tru_gia_canh = models.FloatField(default=0)
    trich_bhxh = models.FloatField(default=0)
    trich_bhyt = models.FloatField(default=0)
    trich_bhtn = models.FloatField(default=0)
    thu_nhap_chiu_thue = models.FloatField(default=0)
    thue_tncn = models.FloatField(default=0)
    tam_ung_khau_tru = models.FloatField(default=0)
    tong_khau_tru = models.FloatField(default=0) 
    thuc_linh_net = models.FloatField(default=0)

    # Thông tin chuyển khoản (mới thêm)
    phuong_thuc_tra_luong = models.CharField(max_length=20, default='Tiền mặt', choices=[
        ('Tiền mặt', 'Tiền mặt'),
        ('Chuyển khoản', 'Chuyển khoản')
    ])
    ngay_chuyen_khoan = models.DateTimeField(blank=True, null=True)
    ma_giao_dich = models.CharField(max_length=50, blank=True, null=True)
    trang_thai_chuyen_khoan = models.CharField(max_length=20, default='Chưa chuyển', choices=[
        ('Chưa chuyển', 'Chưa chuyển'),
        ('Đang xử lý', 'Đang xử lý'),
        ('Thành công', 'Thành công'),
        ('Thất bại', 'Thất bại')
    ])
    ghi_chu_chuyen_khoan = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'bangluong_chitiet'
        unique_together = (('manhanvien', 'thang_luong'),)

# --- MODEL NGHỈ PHÉP (ĐÃ FIX KHÓA CHÍNH) ---

class NghiPhep(models.Model):
    # Sử dụng 'manghiphep' làm khóa chính, khớp với SQL database
    # db_column='manghiphep' đảm bảo Django ánh xạ đúng cột trong DB
    manghiphep = models.AutoField(primary_key=True, db_column='manghiphep') 

    manhanvien = models.ForeignKey('NhanVien', on_delete=CASCADE, db_column='manhanvien')
    ngaybatdau = models.DateField()
    ngayketthuc = models.DateField()
    lydo = models.TextField(blank=True, null=True)  # TEXT trong SQL
    trangthai = models.CharField(default='Đang chờ', max_length=50)  # VARCHAR(50) trong SQL

    class Meta:
        db_table = 'nghiphep'
        verbose_name = 'Đơn Nghỉ Phép'
        verbose_name_plural = 'Đơn Nghỉ Phép'

# --- CÁC MODEL PHỤ KHÁC (GIỮ NGUYÊN) ---

class ChiTietLuong(models.Model):
    machitietluong = models.AutoField(primary_key=True)
    manhanvien = models.ForeignKey(NhanVien, on_delete=CASCADE, db_column='manhanvien')
    thangluong = models.DateField()
    tienthuong = models.FloatField(default=0)
    tienphat = models.FloatField(default=0)
    tongluong = models.FloatField()
    class Meta:
        db_table = 'chitietluong'

class KhenThuongKyLuat(models.Model):
    maktkl = models.AutoField(primary_key=True)
    manhanvien = models.ForeignKey(NhanVien, on_delete=CASCADE, db_column='manhanvien')
    loai = models.CharField(max_length=20) 
    lydo = models.CharField(blank=True, max_length=200, null=True)
    sotien = models.FloatField(default=0)
    ngaythuchien = models.DateField(auto_now_add=True)
    class Meta:
        db_table = 'khenthuongkyluat'

class QuanLyNhapLieu(models.Model):
    malog = models.AutoField(primary_key=True)
    nguoinhap = models.ForeignKey(TaiKhoan, on_delete=SET_NULL, db_column='nguoinhap', to_field='tendangnhap', blank=True, null=True)
    bangdulieu = models.CharField(max_length=50)
    thoigiannhap = models.DateTimeField(auto_now_add=True)
    giatricu = models.TextField(blank=True, null=True)
    giatrimoi = models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'quanlynhaplieu'


class ChamCong(models.Model):
    machamcong = models.AutoField(primary_key=True)
    manhanvien = models.ForeignKey(NhanVien, on_delete=CASCADE, db_column='manhanvien')
    ngay = models.DateField()
    gio_vao = models.TimeField(null=True, blank=True)
    gio_ra = models.TimeField(null=True, blank=True)
    phut_di_muon = models.IntegerField(default=0)
    trangthai = models.CharField(max_length=50, default='Đang làm việc')
    ghi_chu = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'chamcong'
        verbose_name = 'Chấm Công'
        verbose_name_plural = 'Quản Lý Chấm Công'
        unique_together = (('manhanvien', 'ngay'),)


class TuyenDung(models.Model):
    ma_job = models.CharField(max_length=30, primary_key=True)
    vi_tri_cong_viec = models.CharField(max_length=200)
    
    # Liên kết khóa ngoại
    maphongban = models.ForeignKey(PhongBan, on_delete=SET_NULL, db_column='maphongban', null=True)
    nguoi_tuyen_dung = models.ForeignKey(NhanVien, on_delete=SET_NULL, db_column='nguoi_tuyen_dung', null=True)
    
    so_luong_tuyen = models.IntegerField(default=1)
    ngay_mo_don = models.DateField(null=True)
    ngay_onboard_du_kien = models.DateField(null=True)
    
    muc_luong_du_kien = models.FloatField(default=0)
    trang_thai = models.CharField(max_length=50, default='Đang mở') # Đang mở, Đã đóng, Tạm dừng, Đã huỷ
    
    mo_ta_cong_viec = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'tuyendung'
        verbose_name = 'Tuyển Dụng'
        verbose_name_plural = 'Tuyển Dụng'


# MODEL ỨNG VIÊN (MỚI)
class UngVien(models.Model):
    ma_ung_vien = models.CharField(max_length=30, primary_key=True)
    ho_ten = models.CharField(max_length=100)
    ngay_sinh = models.DateField(null=True, blank=True)
    gioi_tinh = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    sdt = models.CharField(max_length=15, null=True, blank=True)
    dia_chi = models.CharField(max_length=200, default='Tòa nhà Bitexco Financial Tower, số 2 Hải Triều, Bến Nghé, Quận 1, TP.HCM')
    
    ma_job = models.ForeignKey(TuyenDung, on_delete=SET_NULL, db_column='ma_job', null=True, blank=True)
    ngay_ung_tuyen = models.DateField(auto_now_add=True)
    
    giai_doan = models.CharField(max_length=50, default='Sơ loại') # Phỏng vấn, Kiểm tra...
    trang_thai = models.CharField(max_length=50, default='Đang xử lý') # Tuyển dụng, Không tuyển...

    ngay_pv = models.DateField(null=True, blank=True)
    gio_pv = models.TimeField(null=True, blank=True)
    dia_diem_pv = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'ungvien'
        verbose_name = 'Danh Sách Ứng Viên'
        verbose_name_plural = 'Danh Sách Ứng Viên'


# MODEL LỊCH SỬ CHUYỂN KHOẢN LƯƠNG (MỚI)
class LichSuChuyenKhoan(models.Model):
    ma_giao_dich = models.CharField(max_length=50, primary_key=True)
    bang_luong = models.ForeignKey(ChiTietBangLuong, on_delete=CASCADE, related_name='lich_su_chuyen_khoan')
    
    so_tien_chuyen = models.FloatField()
    phi_chuyen_khoan = models.FloatField(default=0)
    so_tien_thuc_nhan = models.FloatField()
    
    ngay_tao_lenh = models.DateTimeField(auto_now_add=True)
    ngay_thuc_hien = models.DateTimeField(blank=True, null=True)
    
    ngan_hang_nhan = models.CharField(max_length=100)
    so_tk_nhan = models.CharField(max_length=50)
    ten_tk_nhan = models.CharField(max_length=100)
    
    trang_thai = models.CharField(max_length=20, default='Chờ xử lý', choices=[
        ('Chờ xử lý', 'Chờ xử lý'),
        ('Đang xử lý', 'Đang xử lý'),
        ('Thành công', 'Thành công'),
        ('Thất bại', 'Thất bại'),
        ('Đã hủy', 'Đã hủy')
    ])
    
    ma_tham_chieu_ngan_hang = models.CharField(max_length=100, blank=True, null=True)
    ly_do_that_bai = models.TextField(blank=True, null=True)
    nguoi_thuc_hien = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'lichsu_chuyenkhoan'
        verbose_name = 'Lịch Sử Chuyển Khoản'
        verbose_name_plural = 'Lịch Sử Chuyển Khoản'
        ordering = ['-ngay_tao_lenh']