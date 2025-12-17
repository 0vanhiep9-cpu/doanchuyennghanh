from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# ĐÃ SỬA LỖI NAMERROR: Import đầy đủ F và FloatField
from django.db.models import Count, Q, Value as V, FloatField, F 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
# Thêm ChiTietBangLuong và LichSuChuyenKhoan vào import
from .models import NhanVien, PhongBan, TaiKhoan, HopDong, ChucVu, Luong, ChiTietBangLuong, KhenThuongKyLuat, NghiPhep, ChamCong, TuyenDung, UngVien, LichSuChuyenKhoan
import datetime
import uuid

# --- HÀM HỖ TRỢ ---

def get_user_vaitro(user):
    if user.is_authenticated:
        try: return TaiKhoan.objects.get(tendangnhap=user.username).vaitro
        except: return 'NhanVien' if not user.is_superuser else 'Admin'
    return 'Guest'

# 1. Trang Đăng Ký
def register_view(request):
    """Xử lý logic đăng ký người dùng mới, tạo cả NhanVien và TaiKhoan."""
    if request.method == 'POST':
        hoten = request.POST.get('hoten')
        tendangnhap = request.POST.get('tendangnhap')
        matkhau = request.POST.get('password')
        email = request.POST.get('email')
        sdt = request.POST.get('sdt')

        # Validation dữ liệu đăng ký
        from .utils import validate_registration_data
        validation_errors = validate_registration_data({
            'hoten': hoten,
            'tendangnhap': tendangnhap,
            'password': matkhau,
            'email': email,
            'sdt': sdt
        })
        
        if validation_errors:
            for error in validation_errors:
                messages.error(request, error)
            return render(request, 'nhanvien/register.html')

        if TaiKhoan.objects.filter(tendangnhap=tendangnhap).exists():
            messages.error(request, 'Tên đăng nhập này đã tồn tại.')
            return render(request, 'nhanvien/register.html')
        
        if NhanVien.objects.filter(email=email).exists():
            messages.error(request, 'Email này đã được đăng ký.')
            return render(request, 'nhanvien/register.html')

        try:
            # Tự động tạo Mã nhân viên (MSxxx)
            last_nv = NhanVien.objects.all().order_by('-manhanvien').first()
            if last_nv:
                try:
                    last_id = int(last_nv.manhanvien[2:]) 
                    new_id = f"MS{last_id + 1:03d}"
                except ValueError:
                    new_id = f"MS{NhanVien.objects.count() + 1:03d}"
            else:
                new_id = "MS001"
            
            # Giả định các khóa ngoại có sẵn (Dựa trên dữ liệu khởi tạo)
            phongban_default = PhongBan.objects.get(maphongban='PB05') 
            chucvu_default = ChucVu.objects.get(machucvu='CV14')
            hopdong_default = HopDong.objects.get(mahopdong='HD03')
            
            # Tạo bản ghi NhanVien mới
            new_nv = NhanVien.objects.create(
                manhanvien=new_id,
                hoten=hoten,
                email=email,
                sdt=sdt,
                maphongban=phongban_default, 
                machucvu=chucvu_default,
                mahopdong=hopdong_default,
                ngaynhap=datetime.date.today(), 
                trangthai='Đang làm',
                gioitinh='Chưa rõ',
            )
            
            # Tạo bản ghi TaiKhoan mới (Lưu mật khẩu plaintext)
            TaiKhoan.objects.create(
                tendangnhap=tendangnhap,
                matkhau=matkhau, # LƯU MẬT KHẨU PLAINTEXT
                manhanvien=new_nv,
                vaitro='NhanVien', 
                trangthai=True,
                trang_thai_duyet='Chờ duyệt'  # Mặc định chờ duyệt
            )
            
            messages.success(request, 'Đăng ký thành công! Tài khoản của bạn đang chờ admin phê duyệt. Bạn sẽ nhận được thông báo khi tài khoản được kích hoạt.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Đăng ký thất bại. Lỗi: Vui lòng kiểm tra dữ liệu khởi tạo trong DB.')
            return render(request, 'nhanvien/register.html')

    return render(request, 'nhanvien/register.html')

# 2. Trang Đăng Nhập (ĐÃ CỐ ĐỊNH)
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user_auth = None
        
        # 1. Xác thực bằng Custom Logic (TaiKhoan plaintext)
        try:
            taikhoan = TaiKhoan.objects.get(tendangnhap=username, matkhau=password)
            
            # Kiểm tra trạng thái phê duyệt
            if taikhoan.trang_thai_duyet == 'Chờ duyệt':
                messages.error(request, 'Tài khoản của bạn đang chờ admin phê duyệt. Vui lòng liên hệ bộ phận nhân sự để được hỗ trợ.')
                return render(request, 'nhanvien/login.html', {'form': AuthenticationForm()})
            elif taikhoan.trang_thai_duyet == 'Từ chối':
                ly_do = taikhoan.ly_do_tu_choi or 'Không có lý do cụ thể'
                messages.error(request, f'Tài khoản của bạn đã bị từ chối. Lý do: {ly_do}')
                return render(request, 'nhanvien/login.html', {'form': AuthenticationForm()})
            
            user_auth, created = User.objects.get_or_create(username=username)
            
            # CẤP QUYỀN TRUY CẬP ADMIN CHO USER GIẢ LẬP
            is_admin = (taikhoan.vaitro == 'Admin')
            
            if user_auth.is_staff != is_admin or user_auth.is_superuser != is_admin:
                user_auth.is_staff = is_admin
                user_auth.is_superuser = is_admin
                user_auth.save()
            
        except TaiKhoan.DoesNotExist:
            # 2. Thử dùng Superuser Django mặc định (mật khẩu hashed)
            user_auth = authenticate(request, username=username, password=password)
            
        # 3. Kiểm tra user_auth và tạo session
        if user_auth is not None and user_auth.is_active:
            login(request, user_auth)
            
            # Dùng hàm cố định đã sửa để xác định vai trò CHÍNH XÁC
            vaitro = get_user_vaitro(user_auth)
            
            # Chuyển hướng
            if vaitro == 'Admin':
                return redirect('dashboard')
            elif vaitro == 'QuanLy':
                return redirect('manager_dashboard')
            else: # Bao gồm cả NhanVien
                return redirect('employee_dashboard')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
            
    form = AuthenticationForm()
    return render(request, 'nhanvien/login.html', {'form': form})


# 3. Trang Đăng Xuất
def logout_view(request):
    logout(request)
    return redirect('login') 

# 4. Chuyển hướng Dashboard (Dựa trên vai trò)
@login_required(login_url='login')
def dashboard_router(request):
    vaitro = get_user_vaitro(request.user) 

    if vaitro == 'Admin':
        return admin_dashboard(request)
    elif vaitro == 'QuanLy':
        return manager_dashboard(request)
    else:
        return employee_dashboard(request)

# 5. Dashboard Admin
@login_required(login_url='login')
def admin_dashboard(request):
    total_employees = NhanVien.objects.filter(trangthai='Đang làm').count()
    total_departments = PhongBan.objects.count()
    
    dept_data_qs = NhanVien.objects.filter(trangthai='Đang làm').values('maphongban__tenphongban').annotate(count=Count('manhanvien'))
    dept_data = [{'name': item['maphongban__tenphongban'], 'count': item['count']} for item in dept_data_qs]
    
    gender_stats = NhanVien.objects.filter(trangthai='Đang làm').aggregate(
        male=Count('manhanvien', filter=Q(gioitinh='Nam')),
        female=Count('manhanvien', filter=Q(gioitinh='Nữ'))
    )
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'dept_data': dept_data,
        'gender_stats': gender_stats,
    }
    return render(request, 'nhanvien/admin_dashboard.html', context)


# 6. Dashboard Quản Lý
@login_required(login_url='login')
def manager_dashboard(request):
    context = {}
    return render(request, 'nhanvien/manager_dashboard.html', context)

# 7. Dashboard Nhân Viên
@login_required(login_url='login')
def employee_dashboard(request):
    try:
        nhanvien = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
        hoten = nhanvien.hoten 
    except NhanVien.DoesNotExist:
        hoten = request.user.username 

    context = {
        'hoten': hoten
    }
    return render(request, 'nhanvien/employee_dashboard.html', context)

# 8. Danh Sách Nhân Viên
@login_required(login_url='login')
def danh_sach_nhan_vien(request):
    # Cho phép ai cũng vào xem, nhưng lấy vai trò để ẩn nút ở template
    vaitro = get_user_vaitro(request.user)

    nhanviens_list = NhanVien.objects.all().select_related('maphongban', 'machucvu').order_by('manhanvien')
    phongbans = PhongBan.objects.all().order_by('tenphongban')

    # BƯỚC 2: Xử lý Filter (Nếu có)
    query = request.GET.get('q')
    phongban_filter = request.GET.get('phongban')
    
    if query:
        # Lọc theo tên hoặc mã nhân viên
        nhanviens_list = nhanviens_list.filter(
            Q(hoten__icontains=query) |
            Q(manhanvien__icontains=query)
        )

    if phongban_filter:
        # Lọc theo phòng ban
        nhanviens_list = nhanviens_list.filter(maphongban__maphongban=phongban_filter)
        
    # BƯỚC 3: TRUYỀN DỮ LIỆU VÀO CONTEXT
    context = {
        'nhanviens': nhanviens_list,
        'phongbans': phongbans,
        'vaitro': vaitro, # <--- QUAN TRỌNG: Truyền vai trò xuống template
    }
    return render(request, 'nhanvien/danh_sach.html', context)

# 9. Hồ Sơ Cá Nhân (Tất cả)
@login_required(login_url='login')
def ho_so_ca_nhan(request):
    try:
        nhanvien = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
    except NhanVien.DoesNotExist:
        return render(request, 'nhanvien/ho_so.html', {'nhanvien': None, 'error': 'Không tìm thấy hồ sơ nhân viên'})
    
    context = {
        'nhanvien': nhanvien
    }
    return render(request, 'nhanvien/ho_so.html', context)

# 10. Chi Tiết Nhân Viên
@login_required(login_url='login')
def chi_tiet_nhan_vien(request, manhanvien):
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        return redirect('employee_dashboard')
        
    nhanvien = get_object_or_404(NhanVien, manhanvien=manhanvien)
    context = {
        'nhanvien': nhanvien
    }
    return render(request, 'nhanvien/ho_so.html', context)

# 11. Chỉnh Sửa Nhân Viên (Admin/Manager)
@login_required(login_url='login')
def chinh_sua_nhan_vien(request, manhanvien):
    vaitro = get_user_vaitro(request.user)
    if vaitro == 'NhanVien': 
        return redirect('danh_sach_nhan_vien')

    nhanvien = get_object_or_404(NhanVien, manhanvien=manhanvien)
    phongbans = PhongBan.objects.all()
    chucvus = ChucVu.objects.all()
    hopdongs = HopDong.objects.all()
    
    if request.method == 'POST':
        try:
            # 1. Cập nhật dữ liệu từ form POST
            nhanvien.hoten = request.POST.get('hoten')
            nhanvien.ngaysinh = request.POST.get('ngaysinh')
            nhanvien.gioitinh = request.POST.get('gioitinh')
            nhanvien.sdt = request.POST.get('sdt')
            nhanvien.diachihientai = request.POST.get('diachihientai')
            nhanvien.cccd = request.POST.get('cccd')
            # Validation email trước khi cập nhật
            new_email = request.POST.get('email')
            if not new_email.endswith('@gmail.com'):
                messages.error(request, 'Email phải có đuôi @gmail.com')
                return render(request, 'nhanvien/chinh_sua_nhan_vien.html', context)
            
            nhanvien.email = new_email
            nhanvien.trinhdototnghiep = request.POST.get('trinhdototnghiep')
            nhanvien.ngaynhap = request.POST.get('ngaynhap')
            
            # Xử lý trường ngày nghỉ có thể là None
            ngaynghi_value = request.POST.get('ngaynghi')
            nhanvien.ngaynghi = ngaynghi_value if ngaynghi_value else None
            
            nhanvien.trangthai = request.POST.get('trangthai')
            
            # Cập nhật thông tin ngân hàng
            nhanvien.ten_ngan_hang = request.POST.get('ten_ngan_hang')
            nhanvien.so_tai_khoan = request.POST.get('so_tai_khoan')
            nhanvien.chu_tai_khoan = request.POST.get('chu_tai_khoan')
            nhanvien.chi_nhanh = request.POST.get('chi_nhanh')
            
            # Xử lý upload ảnh
            if 'thongtinanh' in request.FILES:
                import os
                from django.core.files.storage import default_storage
                
                uploaded_file = request.FILES['thongtinanh']
                # Tạo tên file unique
                file_extension = os.path.splitext(uploaded_file.name)[1]
                new_filename = f"avatar_{nhanvien.manhanvien}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
                
                # Lưu file vào thư mục media/avatars/
                file_path = default_storage.save(f'avatars/{new_filename}', uploaded_file)
                
                # Lưu tên file vào database
                nhanvien.thongtinanh = new_filename
            
            # 2. Cập nhật các khóa ngoại
            nhanvien.maphongban_id = request.POST.get('maphongban')
            nhanvien.machucvu_id = request.POST.get('machucvu')
            nhanvien.mahopdong_id = request.POST.get('mahopdong')
            
            # 3. Lưu
            nhanvien.save()
            messages.success(request, f'Cập nhật hồ sơ {manhanvien} thành công!')
            return redirect('chi_tiet_nhan_vien', manhanvien=nhanvien.manhanvien)
            
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật hồ sơ: {e}')
            
    context = {
        'nhanvien': nhanvien,
        'phongbans': phongbans,
        'chucvus': chucvus,
        'hopdongs': hopdongs,
        'is_adding': False # Đảm bảo form hiển thị chế độ chỉnh sửa
    }
    return render(request, 'nhanvien/chinh_sua_nhan_vien.html', context)

# 12. Thêm Mới Nhân Viên (Admin/Manager)
@login_required(login_url='login')
def them_moi_nhan_vien(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro == 'NhanVien': 
        return redirect('danh_sach_nhan_vien')

    phongbans = PhongBan.objects.all()
    chucvus = ChucVu.objects.all()
    hopdongs = HopDong.objects.all()
    
    # Kiểm tra phương thức POST để lưu dữ liệu
    if request.method == 'POST':
        try:
            # 1. Tự động tạo Mã nhân viên (MSxxx)
            last_nv = NhanVien.objects.all().order_by('-manhanvien').first()
            if last_nv:
                try:
                    last_id = int(last_nv.manhanvien[2:]) 
                    new_id = f"MS{last_id + 1:03d}"
                except ValueError:
                    new_id = f"MS{NhanVien.objects.count() + 1:03d}"
            else:
                new_id = "MS001"
            
            # 2. Tạo bản ghi NhanVien mới
            new_nv = NhanVien.objects.create(
                manhanvien=new_id,
                hoten=request.POST.get('hoten'),
                ngaysinh=request.POST.get('ngaysinh') or None,
                gioitinh=request.POST.get('gioitinh'),
                sdt=request.POST.get('sdt'),
                diachihientai=request.POST.get('diachihientai'),
                cccd=request.POST.get('cccd'),
                email=request.POST.get('email'),
                trinhdototnghiep=request.POST.get('trinhdototnghiep'),
                ngaynhap=request.POST.get('ngaynhap'),
                ngaynghi=request.POST.get('ngaynghi') or None,
                trangthai=request.POST.get('trangthai'),
                # Thông tin ngân hàng
                ten_ngan_hang=request.POST.get('ten_ngan_hang'),
                so_tai_khoan=request.POST.get('so_tai_khoan'),
                chu_tai_khoan=request.POST.get('chu_tai_khoan'),
                chi_nhanh=request.POST.get('chi_nhanh'),
                # Khóa ngoại
                maphongban_id=request.POST.get('maphongban'),
                machucvu_id=request.POST.get('machucvu'),
                mahopdong_id=request.POST.get('mahopdong'),
            )
            
            # Xử lý upload ảnh cho nhân viên mới
            if 'thongtinanh' in request.FILES:
                new_nv.thongtinanh = request.FILES['thongtinanh']
                new_nv.save()
            
            messages.success(request, f'Thêm mới nhân viên {new_id} thành công!')
            return redirect('danh_sach_nhan_vien')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi thêm mới hồ sơ: {e}')
            
    # GET request: Hiển thị form trống
    context = {
        'phongbans': phongbans,
        'chucvus': chucvus,
        'hopdongs': hopdongs,
        'nhanvien': None, # Dùng None để template biết đây là chế độ THÊM MỚI
        'is_adding': True
    }
    return render(request, 'nhanvien/chinh_sua_nhan_vien.html', context)


# 13. Quản Lý Phòng Ban (Admin/Manager)
@login_required(login_url='login')
def quanly_phong_ban_view(request):
    # Cho phép ai cũng vào xem
    vaitro = get_user_vaitro(request.user)
    
    phongbans_list = PhongBan.objects.all()

    context = {
        'phongbans': phongbans_list,
        'vaitro': vaitro # <--- QUAN TRỌNG
    }
    return render(request, 'nhanvien/phong_ban.html', context)


# 14. QUẢN LÝ LƯƠNG CƠ BẢN (HIỂN THỊ MASTER DATA)
@login_required(login_url='login')
def quanly_luong_view(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': return redirect('employee_dashboard') 

    # Bước 0: Đảm bảo nhân viên có dữ liệu lương Master (cho NV mới)
    for nv in NhanVien.objects.all():
        Luong.objects.get_or_create(
            manhanvien=nv,
            defaults={'luong_hop_dong': 15000000, 'phucap_antrua': 0, 'phucap_xangxe': 0, 'phucap_khac': 0, 'so_nguoi_phu_thuoc': 0}
        )

    # Bước 1: Query (Lấy Master Data)
    nhanviens_qs = NhanVien.objects.filter(trangthai='Đang làm').select_related('machucvu', 'luong').all()
    
    query = request.GET.get('q')
    if query:
        nhanviens_qs = nhanviens_qs.filter(Q(hoten__icontains=query) | Q(manhanvien__icontains=query))
    
    luong_data = []
    for nv in nhanviens_qs:
        luong_info = getattr(nv, 'luong', None)
        
        # SỬA LỖI TRUY VẤN: Lấy luong_hop_dong
        lcb = luong_info.luong_hop_dong if luong_info else 0.0
        
        # Tính tổng phụ cấp
        tong_pc = (luong_info.phucap_antrua if luong_info else 0) + \
                  (luong_info.phucap_xangxe if luong_info else 0) + \
                  (luong_info.phucap_khac if luong_info else 0)

        luong_data.append({
            'manhanvien': nv.manhanvien,
            'hoten': nv.hoten,
            'chucvu_ten': nv.machucvu.tenchucvu if nv.machucvu else '',
            'luong_cb': lcb, 
            'he_so': luong_info.hesoluong if luong_info else 1.0, 
            'tong_phucap': tong_pc, 
            'bh_phan_tram': 10.5,
        })

    return render(request, 'nhanvien/quanly_luong.html', {'luong_data': luong_data, 'query': query})


# 15. TÍNH LƯƠNG PAYROLL (Đồng bộ với cấu trúc mới)
@login_required(login_url='login')
def tinh_luong_payroll(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': return redirect('employee_dashboard')

    thang_hien_tai = datetime.date(2025, 8, 1) # Cố định tháng 8 cho demo
    
    nhanviens_qs = NhanVien.objects.filter(trangthai='Đang làm').select_related('luong').order_by('manhanvien')

    if request.method == 'POST':
        for nv in nhanviens_qs:
            cong_thuc_te = float(request.POST.get(f'cong_thuc_te_{nv.manhanvien}', 26))
            cong_ot = float(request.POST.get(f'cong_ot_{nv.manhanvien}', 0))
            
            luong_master = getattr(nv, 'luong', None)

            # Lấy Master Data
            lcb_hd = luong_master.luong_hop_dong if luong_master else 15000000
            pc_antrua = luong_master.phucap_antrua if luong_master else 0
            pc_xangxe = luong_master.phucap_xangxe if luong_master else 0
            pc_khac = luong_master.phucap_khac if luong_master else 0
            nguoi_pt = luong_master.so_nguoi_phu_thuoc if luong_master else 0
            
            # --- TÍNH TOÁN ---
            luong_ngay = lcb_hd / 26
            luong_thuc_te = luong_ngay * cong_thuc_te
            luong_ot_tien = (luong_ngay / 8) * 1.5 * cong_ot
            
            bhxh_tien = lcb_hd * 0.08
            bhyt_tien = lcb_hd * 0.015
            bhtn_tien = lcb_hd * 0.01
            tong_bh = bhxh_tien + bhyt_tien + bhtn_tien
            
            gross = luong_thuc_te + luong_ot_tien + pc_antrua + pc_xangxe + pc_khac
            
            giam_tru = 11000000 + (nguoi_pt * 4400000)
            tn_chiu_thue = max(0, gross - tong_bh - giam_tru)
            thue_tncn = tn_chiu_thue * 0.05
            
            tong_khau_tru = tong_bh + thue_tncn
            net = gross - tong_khau_tru
            
            # --- LƯU VÀO DB (SỬ DỤNG TÊN CỘT CHUẨN) ---
            ChiTietBangLuong.objects.update_or_create(
                manhanvien=nv,
                thang_luong=thang_hien_tai,
                defaults={
                    'cong_thuc_te': cong_thuc_te, 'cong_ot': cong_ot, 'cong_chuan': 26,
                    'nghi_co_luong': 0, 'nghi_khong_luong': 0, 
                    
                    'luong_co_ban_thuc_lanh': luong_thuc_te, 
                    'luong_ot': luong_ot_tien, 'thuong_kpi': 0,
                    
                    'phu_cap_antrua': pc_antrua, 'phu_cap_xang_xe': pc_xangxe, 'phu_cap_khac': pc_khac, 
                    
                    'tong_thu_nhap_gross': gross,
                    'giam_tru_gia_canh': giam_tru,
                    'trich_bhxh': bhxh_tien, 'trich_bhyt': bhyt_tien, 'trich_bhtn': bhtn_tien,
                    'thu_nhap_chiu_thue': tn_chiu_thue, 'thue_tncn': thue_tncn,
                    
                    'tong_khau_tru': tong_khau_tru, 
                    'thuc_linh_net': net
                }
            )
        messages.success(request, "Đã cập nhật bảng lương.")
        return redirect('tinh_luong_payroll')

    # GET: Hiển thị
    bang_luong_da_tinh = ChiTietBangLuong.objects.filter(
        thang_luong=thang_hien_tai
    ).select_related('manhanvien').order_by('manhanvien__manhanvien')

    context = {'thang_hien_tai': thang_hien_tai, 'nhanviens': nhanviens_qs, 'bang_luong_da_tinh': bang_luong_da_tinh}
    return render(request, 'nhanvien/tinh_luong_payroll.html', context)


# 19. Bảng Lương Cá Nhân (Tất cả user)
@login_required(login_url='login')
def luong_ca_nhan_view(request):
    # Lấy thông tin lương chi tiết (bangluong_chitiet) của nhân viên đang đăng nhập
    try:
        nhanvien_obj = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
        # Lấy bảng lương gần nhất
        bang_luong = ChiTietBangLuong.objects.filter(ma_nhan_vien=nhanvien_obj).order_by('-thang_luong').first()
    except:
        bang_luong = None

    context = {
        'bang_luong': bang_luong
    }
    return render(request, 'nhanvien/luong_thuong.html', context)


# 20. Chi Tiết Phòng Ban (Admin/Manager)
@login_required(login_url='login')
def chitiet_phong_ban(request, maphongban):
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        return redirect('employee_dashboard')

    # 1. Lấy thông tin phòng ban
    phongban = get_object_or_404(PhongBan, maphongban=maphongban)
    
    # 2. Lấy danh sách nhân viên trong phòng ban đó
    nhanviens_phong = NhanVien.objects.filter(
        maphongban=phongban
    ).select_related('machucvu').order_by('manhanvien')
    
    # 3. Lấy danh sách tất cả chức vụ cho chức năng Thêm NV
    chucvus = ChucVu.objects.all()

    context = {
        'phongban': phongban,
        'nhanviens_phong': nhanviens_phong,
        'chucvus': chucvus,
        'is_admin': (vaitro == 'Admin')
    }
    return render(request, 'nhanvien/chitiet_phongban.html', context)


# 21. Chỉnh Sửa Phòng Ban (Admin/Manager)
@login_required(login_url='login')
def chinh_sua_phong_ban(request, maphongban):
    vaitro = get_user_vaitro(request.user)
    if vaitro == 'NhanVien': 
        return redirect('danh_sach_nhan_vien')

    phongban = get_object_or_404(PhongBan, maphongban=maphongban)

    if request.method == 'POST':
        try:
            # 1. Cập nhật dữ liệu từ form POST
            phongban.tenphongban = request.POST.get('tenphongban')
            phongban.diachi = request.POST.get('diachi')
            phongban.sdt = request.POST.get('sdt')
            
            # 2. Lưu
            phongban.save()
            messages.success(request, f'Cập nhật phòng ban {maphongban} thành công!')
            return redirect('quanly_phong_ban')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật phòng ban: {e}')
            
    context = {
        'phongban': phongban,
    }
    return render(request, 'nhanvien/chinh_sua_phong_ban.html', context)


# 22. Thêm Mới Phòng Ban (Admin/Manager)
@login_required(login_url='login')
def them_phong_ban(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro == 'NhanVien': 
        return redirect('danh_sach_nhan_vien')

    if request.method == 'POST':
        try:
            # 1. Tạo Phòng Ban mới
            PhongBan.objects.create(
                maphongban=request.POST.get('maphongban'), # Cần có input maphongban trong form
                tenphongban=request.POST.get('tenphongban'),
                diachi=request.POST.get('diachi'),
                sdt=request.POST.get('sdt')
            )
            messages.success(request, 'Thêm phòng ban mới thành công.')
            return redirect('quanly_phong_ban')
        except Exception as e:
            messages.error(request, f'Lỗi khi thêm phòng ban: {e}')
            
    # GET request: Hiển thị form trống
    context = {
        'phongban': None,  # Không có đối tượng cũ
        'is_adding': True
    }
    return render(request, 'nhanvien/chinh_sua_phong_ban.html', context)


# 23. Danh sách Khen thưởng / Kỷ luật
@login_required(login_url='login')
def danh_sach_khenthuong_kyluat(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        return redirect('employee_dashboard')

    # Lấy tất cả bản ghi, sắp xếp mới nhất lên đầu
    ktkl_list = KhenThuongKyLuat.objects.select_related('manhanvien').all().order_by('-ngaythuchien')

    # Xử lý tìm kiếm
    query = request.GET.get('q')
    loai_filter = request.GET.get('loai')

    if query:
        ktkl_list = ktkl_list.filter(
            Q(manhanvien__hoten__icontains=query) | 
            Q(manhanvien__manhanvien__icontains=query) |
            Q(lydo__icontains=query)
        )
    
    if loai_filter and loai_filter != 'all':
        ktkl_list = ktkl_list.filter(loai=loai_filter)

    context = {
        'ktkl_list': ktkl_list,
        'query': query,
        'loai_filter': loai_filter
    }
    return render(request, 'nhanvien/khenthuong_kyluat_list.html', context)

# 24. Thêm mới Khen thưởng / Kỷ luật
@login_required(login_url='login')
def them_khenthuong_kyluat(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']: return redirect('employee_dashboard')

    if request.method == 'POST':
        try:
            manhanvien_id = request.POST.get('manhanvien')
            loai = request.POST.get('loai')
            lydo = request.POST.get('lydo')
            sotien = float(request.POST.get('sotien') or 0)
            ngaythuchien = request.POST.get('ngaythuchien')

            # Nếu là Kỷ luật thì số tiền nên là âm (hoặc tùy quy ước, ở đây ta lưu giá trị nhập vào)
            # Nếu muốn tự động chuyển âm cho kỷ luật:
            if loai == 'Kỷ luật' and sotien > 0:
                sotien = -sotien

            KhenThuongKyLuat.objects.create(
                manhanvien_id=manhanvien_id,
                loai=loai,
                lydo=lydo,
                sotien=sotien,
                ngaythuchien=ngaythuchien
            )
            messages.success(request, 'Thêm mới thành công!')
            return redirect('danh_sach_khenthuong_kyluat')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')

    # Lấy danh sách nhân viên để chọn
    nhanviens = NhanVien.objects.filter(trangthai='Đang làm').order_by('manhanvien')
    return render(request, 'nhanvien/khenthuong_kyluat_form.html', {'nhanviens': nhanviens, 'is_adding': True})

# 25. Chỉnh sửa
@login_required(login_url='login')
def sua_khenthuong_kyluat(request, maktkl):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': return redirect('employee_dashboard')

    ktkl = get_object_or_404(KhenThuongKyLuat, maktkl=maktkl)

    if request.method == 'POST':
        try:
            ktkl.loai = request.POST.get('loai')
            ktkl.lydo = request.POST.get('lydo')
            sotien = float(request.POST.get('sotien') or 0)
            
            # Logic giữ nguyên dấu hoặc tự động đổi dấu
            if ktkl.loai == 'Kỷ luật' and sotien > 0: sotien = -sotien
            
            ktkl.sotien = sotien
            ktkl.ngaythuchien = request.POST.get('ngaythuchien')
            ktkl.save()
            
            messages.success(request, 'Cập nhật thành công!')
            return redirect('danh_sach_khenthuong_kyluat')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')

    # Không cho sửa Nhân viên, chỉ sửa nội dung
    return render(request, 'nhanvien/khenthuong_kyluat_form.html', {'item': ktkl, 'is_adding': False})

# 4. Xóa
@login_required(login_url='login')
def xoa_khenthuong_kyluat(request, maktkl):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': 
        messages.error(request, 'Bạn không có quyền xóa.')
        return redirect('danh_sach_khenthuong_kyluat')

    try:
        ktkl = get_object_or_404(KhenThuongKyLuat, maktkl=maktkl)
        ktkl.delete()
        messages.success(request, 'Đã xóa bản ghi thành công.')
    except Exception as e:
        messages.error(request, f'Lỗi khi xóa: {e}')
    
    return redirect('danh_sach_khenthuong_kyluat')

#26 phiếu lương
@login_required(login_url='login')
def in_phieu_luong(request, payroll_id):
    # Lấy bản ghi lương chi tiết, nếu không có thì báo lỗi 404
    payroll = get_object_or_404(ChiTietBangLuong.objects.select_related('manhanvien', 'manhanvien__machucvu', 'manhanvien__maphongban'), id=payroll_id)
    
    nv = payroll.manhanvien
    
    # Chuẩn bị dữ liệu hiển thị (Format tiền tệ sẽ xử lý ở template)
    context = {
        'payroll': payroll,
        'nv': nv,
        'today': datetime.date.today(), # Để hiện ngày in
        'company_name': 'Công ty Harmony', # Hardcode hoặc lấy từ Cấu hình
        'company_address': '50 phường Dịch Vọng, quận Cầu Giấy, Hà Nội',
        'company_web': 'Harmony.std.com',
    }
    
    return render(request, 'nhanvien/phieu_luong.html', context)

# ---------------------------------------------------------
# QUẢN LÝ CHUYỂN KHOẢN LƯƠNG
# ---------------------------------------------------------

# 1. Danh sách chuyển khoản lương (Admin)
@login_required(login_url='login')
def quan_ly_chuyen_khoan_luong(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': 
        return redirect('employee_dashboard')

    # Lấy tháng lương để lọc
    thang_loc = request.GET.get('thang', datetime.date(2025, 8, 1).strftime('%Y-%m-%d'))
    
    # Lấy danh sách bảng lương theo tháng
    bang_luong_list = ChiTietBangLuong.objects.filter(
        thang_luong=thang_loc
    ).select_related('manhanvien').order_by('manhanvien__manhanvien')
    
    # Thống kê
    tong_nhan_vien = bang_luong_list.count()
    tong_tien_luong = sum(bl.thuc_linh_net for bl in bang_luong_list)
    
    # Thống kê theo phương thức
    chuyen_khoan_count = bang_luong_list.filter(phuong_thuc_tra_luong='Chuyển khoản').count()
    tien_mat_count = bang_luong_list.filter(phuong_thuc_tra_luong='Tiền mặt').count()
    
    # Thống kê trạng thái chuyển khoản
    chua_chuyen = bang_luong_list.filter(
        phuong_thuc_tra_luong='Chuyển khoản',
        trang_thai_chuyen_khoan='Chưa chuyển'
    ).count()
    
    thanh_cong = bang_luong_list.filter(
        phuong_thuc_tra_luong='Chuyển khoản',
        trang_thai_chuyen_khoan='Thành công'
    ).count()

    context = {
        'bang_luong_list': bang_luong_list,
        'thang_loc': thang_loc,
        'tong_nhan_vien': tong_nhan_vien,
        'tong_tien_luong': tong_tien_luong,
        'chuyen_khoan_count': chuyen_khoan_count,
        'tien_mat_count': tien_mat_count,
        'chua_chuyen': chua_chuyen,
        'thanh_cong': thanh_cong
    }
    return render(request, 'nhanvien/quan_ly_chuyen_khoan.html', context)

# 2. Cập nhật phương thức trả lương
@login_required(login_url='login')
def cap_nhat_phuong_thuc_tra_luong(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': 
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        payroll_id = request.POST.get('payroll_id')
        phuong_thuc = request.POST.get('phuong_thuc')
        
        try:
            payroll = ChiTietBangLuong.objects.get(id=payroll_id)
            payroll.phuong_thuc_tra_luong = phuong_thuc
            
            # Reset trạng thái nếu chuyển từ chuyển khoản sang tiền mặt
            if phuong_thuc == 'Tiền mặt':
                payroll.trang_thai_chuyen_khoan = 'Chưa chuyển'
                payroll.ngay_chuyen_khoan = None
                payroll.ma_giao_dich = None
            
            payroll.save()
            messages.success(request, f'Đã cập nhật phương thức trả lương cho {payroll.manhanvien.hoten}')
            
        except ChiTietBangLuong.DoesNotExist:
            messages.error(request, 'Không tìm thấy bản ghi lương.')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
    
    return redirect('quan_ly_chuyen_khoan_luong')

# 3. Thực hiện chuyển khoản lương
@login_required(login_url='login')
def thuc_hien_chuyen_khoan_luong(request):
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin': 
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        payroll_ids = request.POST.getlist('payroll_ids')
        
        if not payroll_ids:
            messages.error(request, 'Vui lòng chọn ít nhất một nhân viên để chuyển khoản.')
            return redirect('quan_ly_chuyen_khoan_luong')
        
        thanh_cong = 0
        that_bai = 0
        
        for payroll_id in payroll_ids:
            try:
                payroll = ChiTietBangLuong.objects.select_related('manhanvien').get(id=payroll_id)
                nv = payroll.manhanvien
                
                # Kiểm tra thông tin ngân hàng
                if not all([nv.ten_ngan_hang, nv.so_tai_khoan, nv.chu_tai_khoan]):
                    messages.warning(request, f'{nv.hoten}: Thiếu thông tin ngân hàng')
                    that_bai += 1
                    continue
                
                # Tạo mã giao dịch
                ma_gd = f"PAY{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"
                
                # Tính phí chuyển khoản (ví dụ 5000 VNĐ)
                phi_ck = 5000
                so_tien_thuc_nhan = payroll.thuc_linh_net - phi_ck
                
                # Tạo lịch sử chuyển khoản
                lich_su = LichSuChuyenKhoan.objects.create(
                    ma_giao_dich=ma_gd,
                    bang_luong=payroll,
                    so_tien_chuyen=payroll.thuc_linh_net,
                    phi_chuyen_khoan=phi_ck,
                    so_tien_thuc_nhan=so_tien_thuc_nhan,
                    ngan_hang_nhan=nv.ten_ngan_hang,
                    so_tk_nhan=nv.so_tai_khoan,
                    ten_tk_nhan=nv.chu_tai_khoan,
                    trang_thai='Đang xử lý',
                    nguoi_thuc_hien=request.user.username
                )
                
                # Cập nhật trạng thái bảng lương
                payroll.trang_thai_chuyen_khoan = 'Đang xử lý'
                payroll.ma_giao_dich = ma_gd
                payroll.ngay_chuyen_khoan = datetime.datetime.now()
                payroll.save()
                
                # Giả lập xử lý chuyển khoản (trong thực tế sẽ gọi API ngân hàng)
                import random
                if random.choice([True, True, True, False]):  # 75% thành công
                    lich_su.trang_thai = 'Thành công'
                    lich_su.ngay_thuc_hien = datetime.datetime.now()
                    lich_su.ma_tham_chieu_ngan_hang = f"REF{random.randint(100000, 999999)}"
                    payroll.trang_thai_chuyen_khoan = 'Thành công'
                    thanh_cong += 1
                else:
                    lich_su.trang_thai = 'Thất bại'
                    lich_su.ly_do_that_bai = 'Tài khoản không tồn tại hoặc bị khóa'
                    payroll.trang_thai_chuyen_khoan = 'Thất bại'
                    that_bai += 1
                
                lich_su.save()
                payroll.save()
                
            except Exception as e:
                messages.error(request, f'Lỗi xử lý {payroll_id}: {e}')
                that_bai += 1
        
        if thanh_cong > 0:
            messages.success(request, f'Đã chuyển khoản thành công cho {thanh_cong} nhân viên.')
        if that_bai > 0:
            messages.warning(request, f'{that_bai} giao dịch thất bại.')
    
    return redirect('quan_ly_chuyen_khoan_luong')

# 4. Lịch sử chuyển khoản
@login_required(login_url='login')
def lich_su_chuyen_khoan(request):
    vaitro = get_user_vaitro(request.user)
    
    if vaitro == 'Admin':
        # Admin xem tất cả
        lich_su_list = LichSuChuyenKhoan.objects.select_related(
            'bang_luong__manhanvien'
        ).all().order_by('-ngay_tao_lenh')
    else:
        # Nhân viên chỉ xem của mình
        try:
            nv = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
            lich_su_list = LichSuChuyenKhoan.objects.filter(
                bang_luong__manhanvien=nv
            ).order_by('-ngay_tao_lenh')
        except:
            lich_su_list = []
    
    # Bộ lọc trạng thái
    trang_thai_filter = request.GET.get('trang_thai')
    if trang_thai_filter:
        lich_su_list = lich_su_list.filter(trang_thai=trang_thai_filter)
    
    context = {
        'lich_su_list': lich_su_list,
        'vaitro': vaitro,
        'trang_thai_filter': trang_thai_filter
    }
    return render(request, 'nhanvien/lich_su_chuyen_khoan.html', context)


# ---------------------------------------------------------
# QUẢN LÝ NGHỈ PHÉP (ĐÃ SỬA LỖI SORTING)
# ---------------------------------------------------------

# 1. Danh sách Đơn Nghỉ Phép
@login_required(login_url='login')
def nghiphep_list(request):
    vaitro = get_user_vaitro(request.user)
    
    # Lấy dữ liệu
    if vaitro in ['Admin', 'QuanLy']:
        # Sếp xem được tất cả
        # Sắp xếp theo manghiphep giảm dần (mới nhất lên đầu)
        ds_nghiphep = NghiPhep.objects.select_related('manhanvien').all().order_by('-manghiphep')
    else:
        # Nhân viên chỉ xem được của mình
        try:
            nv_hien_tai = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
            ds_nghiphep = NghiPhep.objects.filter(manhanvien=nv_hien_tai).order_by('-manghiphep')
        except NhanVien.DoesNotExist:
            ds_nghiphep = []

    # Bộ lọc trạng thái
    trangthai_filter = request.GET.get('trangthai')
    if trangthai_filter:
        ds_nghiphep = ds_nghiphep.filter(trangthai=trangthai_filter)

    context = {
        'ds_nghiphep': ds_nghiphep,
        'vaitro': vaitro,
        'trangthai_filter': trangthai_filter
    }
    return render(request, 'nhanvien/nghiphep_list.html', context)

# 2. Tạo Đơn Nghỉ Phép Mới
@login_required(login_url='login')
def them_nghiphep(request):
    # Xác định nhân viên đang đăng nhập
    try:
        nv_hien_tai = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
    except NhanVien.DoesNotExist:
        if request.user.is_superuser:
             pass # Admin tạo hộ
        else:
             messages.error(request, 'Bạn chưa có hồ sơ nhân viên để tạo đơn.')
             return redirect('nghiphep_list')

    if request.method == 'POST':
        try:
            # Nếu là Admin/QL tạo hộ, lấy mã NV từ form, nếu là NV thì lấy chính mình
            manhanvien_id = request.POST.get('manhanvien') if get_user_vaitro(request.user) in ['Admin', 'QuanLy'] else nv_hien_tai.manhanvien
            
            ngaybatdau = request.POST.get('ngaybatdau')
            ngayketthuc = request.POST.get('ngayketthuc')
            lydo = request.POST.get('lydo')
            
            # Tạo đơn
            NghiPhep.objects.create(
                manhanvien_id=manhanvien_id,
                ngaybatdau=ngaybatdau,
                ngayketthuc=ngayketthuc,
                lydo=lydo,
                trangthai='Đang chờ'
            )
            messages.success(request, 'Gửi đơn xin nghỉ thành công!')
            return redirect('nghiphep_list')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
    
    # Lấy danh sách nhân viên để Admin chọn (nếu cần)
    nhanviens = NhanVien.objects.filter(trangthai='Đang làm')
    
    return render(request, 'nhanvien/nghiphep_form.html', {
        'nv_hien_tai': nv_hien_tai if 'nv_hien_tai' in locals() else None,
        'nhanviens': nhanviens,
        'is_admin': get_user_vaitro(request.user) in ['Admin', 'QuanLy']
    })

# 3. Phê Duyệt / Từ Chối (Chỉ Admin/QL)
@login_required(login_url='login')
def duyet_nghiphep(request, madon, trangthai_moi):
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('nghiphep_list')

    # Sử dụng manghiphep để tìm kiếm theo khóa chính
    don = get_object_or_404(NghiPhep, manghiphep=madon) 
    
    if trangthai_moi in ['Đã duyệt', 'Từ chối']:
        don.trangthai = trangthai_moi
        don.save()
        messages.success(request, f'Đã chuyển trạng thái đơn thành: {trangthai_moi}')
    
    return redirect('nghiphep_list')



# ---------------------------------------------------------
# MODULE CHẤM CÔNG (TIME ATTENDANCE) - CHỈ QUẢN LÝ PHÒNG BAN
# ---------------------------------------------------------

@login_required(login_url='login')
def chamcong_list(request):
    vaitro = get_user_vaitro(request.user)
    today = datetime.date.today()
    
    # 1. LẤY DỮ LIỆU THEO QUYỀN HẠN MỚI
    if vaitro == 'Admin':
        # Admin: Xem được tất cả phòng ban
        ngay_loc = request.GET.get('date', today)
        chamcong_qs = ChamCong.objects.select_related('manhanvien', 'manhanvien__maphongban').filter(ngay=ngay_loc).order_by('manhanvien__maphongban__tenphongban', 'gio_vao')
        
        # Danh sách nhân viên chưa chấm công (để quản lý chấm hộ)
        nhanviens_chua_cham = NhanVien.objects.filter(
            trangthai='Đang làm'
        ).exclude(
            manhanvien__in=chamcong_qs.values_list('manhanvien', flat=True)
        ).select_related('maphongban').order_by('maphongban__tenphongban', 'manhanvien')
        
        # Thống kê
        di_muon_count = chamcong_qs.filter(phut_di_muon__gt=0).count()
        vanga_mat_count = nhanviens_chua_cham.count()
        
    elif vaitro == 'QuanLy':
        # Quản lý: Chỉ xem nhân viên trong phòng ban của mình
        try:
            nv_quanly = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
            phongban_quanly = nv_quanly.maphongban
            
            ngay_loc = request.GET.get('date', today)
            chamcong_qs = ChamCong.objects.select_related('manhanvien').filter(
                ngay=ngay_loc,
                manhanvien__maphongban=phongban_quanly
            ).order_by('gio_vao')
            
            # Danh sách nhân viên trong phòng chưa chấm công
            nhanviens_chua_cham = NhanVien.objects.filter(
                trangthai='Đang làm',
                maphongban=phongban_quanly
            ).exclude(
                manhanvien__in=chamcong_qs.values_list('manhanvien', flat=True)
            ).order_by('manhanvien')
            
            # Thống kê
            di_muon_count = chamcong_qs.filter(phut_di_muon__gt=0).count()
            vanga_mat_count = nhanviens_chua_cham.count()
            
        except NhanVien.DoesNotExist:
            chamcong_qs = []
            nhanviens_chua_cham = []
            di_muon_count = 0
            vanga_mat_count = 0
            ngay_loc = today
    else:
        # Nhân viên: Chỉ xem lịch sử chấm công của chính mình (KHÔNG ĐƯỢC CHẤM CÔNG)
        try:
            nv = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
            chamcong_qs = ChamCong.objects.filter(manhanvien=nv).order_by('-ngay')
            nhanviens_chua_cham = []
        except:
            chamcong_qs = []
            nhanviens_chua_cham = []
        
        ngay_loc = today
        di_muon_count = 0
        vanga_mat_count = 0

    context = {
        'chamcong_list': chamcong_qs,
        'nhanviens_chua_cham': nhanviens_chua_cham,
        'vaitro': vaitro,
        'today': today,
        'ngay_loc': str(ngay_loc),
        'di_muon_count': di_muon_count,
        'vang_mat': vanga_mat_count
    }
    return render(request, 'nhanvien/chamcong.html', context)

@login_required(login_url='login')
def thuc_hien_cham_cong(request, action):
    """
    Chấm công cho nhân viên - CHỈ ADMIN VÀ QUẢN LÝ PHÒNG BAN
    action: 'checkin_nv' hoặc 'checkout_nv'
    """
    vaitro = get_user_vaitro(request.user)
    
    # Kiểm tra quyền: Chỉ Admin và QuanLy được chấm công
    if vaitro not in ['Admin', 'QuanLy']:
        messages.error(request, 'Bạn không có quyền thực hiện chấm công.')
        return redirect('chamcong_list')
    
    # Lấy mã nhân viên từ POST data
    manhanvien_id = request.POST.get('manhanvien')
    if not manhanvien_id:
        messages.error(request, 'Không tìm thấy mã nhân viên.')
        return redirect('chamcong_list')
    
    try:
        nv = NhanVien.objects.get(manhanvien=manhanvien_id)
        
        # Kiểm tra quyền quản lý phòng ban (nếu là QuanLy)
        if vaitro == 'QuanLy':
            nv_quanly = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
            if nv.maphongban != nv_quanly.maphongban:
                messages.error(request, 'Bạn chỉ có thể chấm công cho nhân viên trong phòng ban của mình.')
                return redirect('chamcong_list')
        
        now = datetime.datetime.now()
        today = now.date()
        current_time = now.time()
        
        # Giờ quy định (8:00 AM)
        gio_lam_viec = datetime.time(8, 0, 0)
        
        if action == 'checkin_nv':
            # Xử lý Check-in cho nhân viên
            if ChamCong.objects.filter(manhanvien=nv, ngay=today).exists():
                messages.warning(request, f'{nv.hoten} đã được chấm công vào hôm nay rồi!')
            else:
                # Tính đi muộn
                phut_muon = 0
                if current_time > gio_lam_viec:
                    dummy_date = datetime.date(2000, 1, 1)
                    dt1 = datetime.datetime.combine(dummy_date, current_time)
                    dt2 = datetime.datetime.combine(dummy_date, gio_lam_viec)
                    phut_muon = int((dt1 - dt2).total_seconds() / 60)

                ChamCong.objects.create(
                    manhanvien=nv,
                    ngay=today,
                    gio_vao=current_time,
                    phut_di_muon=phut_muon,
                    trangthai='Đang làm việc',
                    ghi_chu=f'Chấm công bởi {request.user.username}'
                )
                
                msg = f'Đã chấm công vào cho {nv.hoten} lúc {current_time.strftime("%H:%M")}.'
                if phut_muon > 0:
                    msg += f' (Đi muộn {phut_muon} phút)'
                messages.success(request, msg)

        elif action == 'checkout_nv':
            # Xử lý Check-out cho nhân viên
            cc = ChamCong.objects.filter(manhanvien=nv, ngay=today).first()
            if cc and cc.gio_ra is None:
                cc.gio_ra = current_time
                cc.trangthai = 'Đã về'
                cc.ghi_chu = (cc.ghi_chu or '') + f' | Check-out bởi {request.user.username}'
                cc.save()
                messages.success(request, f'Đã chấm công ra cho {nv.hoten} lúc {current_time.strftime("%H:%M")}.')
            elif cc and cc.gio_ra:
                messages.warning(request, f'{nv.hoten} đã được chấm công ra rồi!')
            else:
                messages.error(request, f'{nv.hoten} chưa được chấm công vào, không thể chấm công ra.')
                
    except NhanVien.DoesNotExist:
        messages.error(request, 'Không tìm thấy nhân viên.')
    except Exception as e:
        messages.error(request, f'Lỗi chấm công: {e}')
        
    return redirect('chamcong_list')


# ---------------------------------------------------------
# TÍNH NĂNG CHO NHÂN VIÊN (CHỈ XEM)
# ---------------------------------------------------------

# 1. Nhân viên xem danh sách phòng ban (chỉ đọc)
@login_required(login_url='login')
def nhanvien_xem_phong_ban(request):
    phongbans = PhongBan.objects.all().order_by('tenphongban')
    
    # Thống kê số nhân viên trong mỗi phòng ban
    phongban_stats = []
    for pb in phongbans:
        so_nv = NhanVien.objects.filter(maphongban=pb, trangthai='Đang làm').count()
        phongban_stats.append({
            'phongban': pb,
            'so_nhanvien': so_nv
        })
    
    context = {
        'phongban_stats': phongban_stats,
        'is_readonly': True  # Đánh dấu chế độ chỉ đọc
    }
    return render(request, 'nhanvien/nhanvien_xem_phongban.html', context)

# 2. Nhân viên xem danh sách đồng nghiệp (chỉ đọc)
@login_required(login_url='login') 
def nhanvien_xem_dong_nghiep(request):
    try:
        # Lấy thông tin nhân viên hiện tại
        nv_hien_tai = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
        
        # Lấy danh sách đồng nghiệp cùng phòng ban
        dong_nghiep = NhanVien.objects.filter(
            maphongban=nv_hien_tai.maphongban,
            trangthai='Đang làm'
        ).exclude(manhanvien=nv_hien_tai.manhanvien).select_related('machucvu').order_by('manhanvien')
        
        # Lấy tất cả nhân viên khác phòng ban (để tham khảo)
        nv_khac_phong = NhanVien.objects.filter(
            trangthai='Đang làm'
        ).exclude(maphongban=nv_hien_tai.maphongban).select_related('maphongban', 'machucvu').order_by('maphongban__tenphongban', 'manhanvien')
        
    except NhanVien.DoesNotExist:
        dong_nghiep = []
        nv_khac_phong = []
        nv_hien_tai = None
    
    context = {
        'nv_hien_tai': nv_hien_tai,
        'dong_nghiep': dong_nghiep,
        'nv_khac_phong': nv_khac_phong,
        'is_readonly': True
    }
    return render(request, 'nhanvien/nhanvien_xem_dongnghiep.html', context)

# 3. Nhân viên xem thông tin tuyển dụng (chỉ đọc)
@login_required(login_url='login')
def nhanvien_xem_tuyen_dung(request):
    # Chỉ hiển thị các vị trí đang mở
    jobs_dang_mo = TuyenDung.objects.filter(
        trang_thai='Đang mở'
    ).select_related('maphongban', 'nguoi_tuyen_dung').order_by('-ngay_mo_don')
    
    context = {
        'jobs': jobs_dang_mo,
        'is_readonly': True
    }
    return render(request, 'nhanvien/nhanvien_xem_tuyendung.html', context)

# 4. Nhân viên xem khen thưởng/kỷ luật của bản thân (chỉ đọc)
@login_required(login_url='login')
def nhanvien_xem_khen_thuong_ky_luat(request):
    try:
        nv_hien_tai = NhanVien.objects.get(taikhoan__tendangnhap=request.user.username)
        
        # Lấy lịch sử khen thưởng/kỷ luật của nhân viên
        lich_su_ktkl = KhenThuongKyLuat.objects.filter(
            manhanvien=nv_hien_tai
        ).order_by('-ngaythuchien')
        
        # Thống kê
        tong_khen_thuong = lich_su_ktkl.filter(loai='Khen thưởng').count()
        tong_ky_luat = lich_su_ktkl.filter(loai='Kỷ luật').count()
        
    except NhanVien.DoesNotExist:
        lich_su_ktkl = []
        tong_khen_thuong = 0
        tong_ky_luat = 0
        nv_hien_tai = None
    
    context = {
        'lich_su_ktkl': lich_su_ktkl,
        'tong_khen_thuong': tong_khen_thuong,
        'tong_ky_luat': tong_ky_luat,
        'nv_hien_tai': nv_hien_tai,
        'is_readonly': True
    }
    return render(request, 'nhanvien/nhanvien_xem_ktkl.html', context)

# ---------------------------------------------------------
# QUẢN LÝ TUYỂN DỤNG (RECRUITMENT) - CHO ADMIN/QUẢN LÝ
# ---------------------------------------------------------

@login_required(login_url='login')
def tuyendung_list(request):
    """Danh sách vị trí tuyển dụng - Admin/QuanLy"""
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        return redirect('employee_dashboard')
    
    # Lấy danh sách job, join với phòng ban và người tuyển dụng
    jobs = TuyenDung.objects.select_related('maphongban', 'nguoi_tuyen_dung').all().order_by('ma_job')
    
    # Thống kê nhanh (Dashboard tuyển dụng)
    total_jobs = jobs.count()
    job_dang_mo = jobs.filter(trang_thai='Đang mở').count()
    total_tuyen = sum(j.so_luong_tuyen for j in jobs) # Tổng số lượng cần tuyển

    context = {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'job_dang_mo': job_dang_mo,
        'total_tuyen': total_tuyen
    }
    return render(request, 'nhanvien/tuyendung_list.html', context)


# ---------------------------------------------------------
# QUẢN LÝ ỨNG VIÊN (CANDIDATES)
# ---------------------------------------------------------

@login_required(login_url='login')
def danh_sach_ung_vien(request):
    # Lấy danh sách và join với Job để lấy tên phòng ban/vị trí
    ungviens = UngVien.objects.select_related('ma_job', 'ma_job__maphongban').all().order_by('ma_ung_vien')
    
    # Lọc theo Job
    job_filter = request.GET.get('job')
    if job_filter:
        ungviens = ungviens.filter(ma_job__ma_job=job_filter)

    jobs = TuyenDung.objects.all() # Để hiển thị dropdown lọc

    context = {
        'ungviens': ungviens,
        'jobs': jobs,
        'job_filter': job_filter
    }
    return render(request, 'nhanvien/ungvien_list.html', context)

@login_required(login_url='login')
def them_ung_vien(request):
    if request.method == 'POST':
        try:
            count = UngVien.objects.count() + 1
            new_id = f"UV{count:03d}"
            
            UngVien.objects.create(
                ma_ung_vien=new_id,
                ho_ten=request.POST.get('ho_ten'),
                ngay_sinh=request.POST.get('ngay_sinh'),
                gioi_tinh=request.POST.get('gioi_tinh'),
                email=request.POST.get('email'),
                sdt=request.POST.get('sdt'),
                ma_job_id=request.POST.get('ma_job'),
                giai_doan=request.POST.get('giai_doan'),
                trang_thai=request.POST.get('trang_thai'),
                ngay_pv=request.POST.get('ngay_pv') or None,
                gio_pv=request.POST.get('gio_pv') or None,
                dia_diem_pv=request.POST.get('dia_diem_pv')
            )
            messages.success(request, 'Thêm ứng viên thành công!')
            return redirect('danh_sach_ung_vien')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')

    jobs = TuyenDung.objects.filter(trang_thai='Đang mở')
    return render(request, 'nhanvien/ungvien_form.html', {'jobs': jobs, 'is_adding': True})

@login_required(login_url='login')
def sua_ung_vien(request, ma_uv):
    uv = get_object_or_404(UngVien, pk=ma_uv)
    
    if request.method == 'POST':
        try:
            uv.ho_ten = request.POST.get('ho_ten')
            uv.ngay_sinh = request.POST.get('ngay_sinh')
            uv.gioi_tinh = request.POST.get('gioi_tinh')
            uv.email = request.POST.get('email')
            uv.sdt = request.POST.get('sdt')
            uv.ma_job_id = request.POST.get('ma_job')
            uv.giai_doan = request.POST.get('giai_doan')
            uv.trang_thai = request.POST.get('trang_thai')
            
            ngay_pv = request.POST.get('ngay_pv')
            uv.ngay_pv = ngay_pv if ngay_pv else None
            
            gio_pv = request.POST.get('gio_pv')
            uv.gio_pv = gio_pv if gio_pv else None
            
            uv.dia_diem_pv = request.POST.get('dia_diem_pv')
            uv.save()
            
            messages.success(request, 'Cập nhật thành công!')
            return redirect('danh_sach_ung_vien')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')

    jobs = TuyenDung.objects.all()
    return render(request, 'nhanvien/ungvien_form.html', {'item': uv, 'jobs': jobs, 'is_adding': False})

@login_required(login_url='login')
def xoa_ung_vien(request, ma_uv):
    try:
        UngVien.objects.get(pk=ma_uv).delete()
        messages.success(request, 'Đã xóa ứng viên.')
    except:
        messages.error(request, 'Lỗi khi xóa.')
    return redirect('danh_sach_ung_vien')


# ---------------------------------------------------------
# QUẢN LÝ PHÊ DUYỆT TÀI KHOẢN (CHỈ ADMIN)
# ---------------------------------------------------------

@login_required(login_url='login')
def quan_ly_phe_duyet_tai_khoan(request):
    """Quản lý phê duyệt tài khoản mới đăng ký"""
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin':
        return redirect('employee_dashboard')
    
    # Lấy danh sách tài khoản chờ duyệt
    tai_khoan_cho_duyet = TaiKhoan.objects.filter(
        trang_thai_duyet='Chờ duyệt'
    ).select_related('manhanvien').order_by('-ngay_tao')
    
    # Lấy danh sách tài khoản đã xử lý (để theo dõi)
    tai_khoan_da_xu_ly = TaiKhoan.objects.filter(
        trang_thai_duyet__in=['Đã duyệt', 'Từ chối']
    ).select_related('manhanvien').order_by('-ngay_duyet')[:20]  # 20 bản ghi gần nhất
    
    # Thống kê
    tong_cho_duyet = tai_khoan_cho_duyet.count()
    tong_da_duyet = TaiKhoan.objects.filter(trang_thai_duyet='Đã duyệt').count()
    tong_tu_choi = TaiKhoan.objects.filter(trang_thai_duyet='Từ chối').count()
    
    context = {
        'tai_khoan_cho_duyet': tai_khoan_cho_duyet,
        'tai_khoan_da_xu_ly': tai_khoan_da_xu_ly,
        'tong_cho_duyet': tong_cho_duyet,
        'tong_da_duyet': tong_da_duyet,
        'tong_tu_choi': tong_tu_choi
    }
    return render(request, 'nhanvien/quan_ly_phe_duyet.html', context)

@login_required(login_url='login')
def phe_duyet_tai_khoan(request, tendangnhap, action):
    """Phê duyệt hoặc từ chối tài khoản"""
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin':
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('quan_ly_phe_duyet_tai_khoan')
    
    try:
        tai_khoan = TaiKhoan.objects.get(tendangnhap=tendangnhap)
        
        if action == 'duyet':
            tai_khoan.trang_thai_duyet = 'Đã duyệt'
            tai_khoan.ngay_duyet = datetime.datetime.now()
            tai_khoan.nguoi_duyet = request.user.username
            tai_khoan.ly_do_tu_choi = None
            tai_khoan.save()
            
            messages.success(request, f'Đã phê duyệt tài khoản {tendangnhap}. Người dùng có thể đăng nhập ngay bây giờ.')
            
        elif action == 'tu_choi':
            ly_do = request.POST.get('ly_do_tu_choi', 'Không đáp ứng yêu cầu')
            
            tai_khoan.trang_thai_duyet = 'Từ chối'
            tai_khoan.ngay_duyet = datetime.datetime.now()
            tai_khoan.nguoi_duyet = request.user.username
            tai_khoan.ly_do_tu_choi = ly_do
            tai_khoan.save()
            
            messages.warning(request, f'Đã từ chối tài khoản {tendangnhap}. Lý do: {ly_do}')
            
    except TaiKhoan.DoesNotExist:
        messages.error(request, 'Không tìm thấy tài khoản.')
    except Exception as e:
        messages.error(request, f'Lỗi: {e}')
    
    return redirect('quan_ly_phe_duyet_tai_khoan')


# ---------------------------------------------------------
# QUẢN LÝ HỢP ĐỒNG (CONTRACT MANAGEMENT)
# ---------------------------------------------------------

@login_required(login_url='login')
def danh_sach_hop_dong(request):
    """Danh sách tất cả hợp đồng"""
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        return redirect('employee_dashboard')
    
    # Lấy danh sách hợp đồng với thông tin nhân viên
    hop_dong_list = HopDong.objects.all().order_by('-ngaybatdau')
    
    # Thêm thông tin nhân viên sử dụng hợp đồng
    hop_dong_data = []
    for hd in hop_dong_list:
        nhan_vien_count = NhanVien.objects.filter(mahopdong=hd).count()
        nhan_vien_list = NhanVien.objects.filter(mahopdong=hd)[:5]  # Lấy 5 nhân viên đầu
        
        hop_dong_data.append({
            'hop_dong': hd,
            'nhan_vien_count': nhan_vien_count,
            'nhan_vien_list': nhan_vien_list,
            'is_expired': hd.ngayketthuc and hd.ngayketthuc < datetime.date.today() if hd.ngayketthuc else False
        })
    
    # Bộ lọc
    loai_filter = request.GET.get('loai')
    trang_thai_filter = request.GET.get('trang_thai')
    
    if loai_filter:
        hop_dong_data = [item for item in hop_dong_data if loai_filter.lower() in item['hop_dong'].loaihopdong.lower()]
    
    if trang_thai_filter == 'het_han':
        hop_dong_data = [item for item in hop_dong_data if item['is_expired']]
    elif trang_thai_filter == 'con_han':
        hop_dong_data = [item for item in hop_dong_data if not item['is_expired']]
    
    # Thống kê
    tong_hop_dong = len(hop_dong_list)
    hop_dong_het_han = len([item for item in hop_dong_data if item['is_expired']])
    hop_dong_con_han = tong_hop_dong - hop_dong_het_han
    
    context = {
        'hop_dong_data': hop_dong_data,
        'tong_hop_dong': tong_hop_dong,
        'hop_dong_het_han': hop_dong_het_han,
        'hop_dong_con_han': hop_dong_con_han,
        'loai_filter': loai_filter,
        'trang_thai_filter': trang_thai_filter,
        'vaitro': vaitro
    }
    return render(request, 'nhanvien/hop_dong_list.html', context)

@login_required(login_url='login')
def chi_tiet_hop_dong(request, mahopdong):
    """Chi tiết hợp đồng và danh sách nhân viên sử dụng"""
    vaitro = get_user_vaitro(request.user)
    if vaitro not in ['Admin', 'QuanLy']:
        return redirect('employee_dashboard')
    
    hop_dong = get_object_or_404(HopDong, mahopdong=mahopdong)
    
    # Danh sách nhân viên sử dụng hợp đồng này
    nhan_vien_list = NhanVien.objects.filter(mahopdong=hop_dong).select_related('maphongban', 'machucvu').order_by('manhanvien')
    
    # Thống kê
    tong_nhan_vien = nhan_vien_list.count()
    nv_dang_lam = nhan_vien_list.filter(trangthai='Đang làm').count()
    nv_da_nghi = nhan_vien_list.filter(trangthai='Đã nghỉ').count()
    
    # Kiểm tra hợp đồng hết hạn
    is_expired = hop_dong.ngayketthuc and hop_dong.ngayketthuc < datetime.date.today() if hop_dong.ngayketthuc else False
    
    context = {
        'hop_dong': hop_dong,
        'nhan_vien_list': nhan_vien_list,
        'tong_nhan_vien': tong_nhan_vien,
        'nv_dang_lam': nv_dang_lam,
        'nv_da_nghi': nv_da_nghi,
        'is_expired': is_expired,
        'vaitro': vaitro
    }
    return render(request, 'nhanvien/hop_dong_detail.html', context)

@login_required(login_url='login')
def them_hop_dong(request):
    """Thêm hợp đồng mới"""
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin':
        return redirect('danh_sach_hop_dong')
    
    if request.method == 'POST':
        try:
            mahopdong = request.POST.get('mahopdong')
            loaihopdong = request.POST.get('loaihopdong')
            ngaybatdau = request.POST.get('ngaybatdau')
            ngayketthuc = request.POST.get('ngayketthuc')
            ghichu = request.POST.get('ghichu')
            
            # Kiểm tra mã hợp đồng đã tồn tại
            if HopDong.objects.filter(mahopdong=mahopdong).exists():
                messages.error(request, f'Mã hợp đồng {mahopdong} đã tồn tại.')
                return render(request, 'nhanvien/hop_dong_form.html', {'is_adding': True})
            
            # Validation ngày
            if ngayketthuc and ngaybatdau:
                if datetime.datetime.strptime(ngayketthuc, '%Y-%m-%d').date() <= datetime.datetime.strptime(ngaybatdau, '%Y-%m-%d').date():
                    messages.error(request, 'Ngày kết thúc phải sau ngày bắt đầu.')
                    return render(request, 'nhanvien/hop_dong_form.html', {'is_adding': True})
            
            HopDong.objects.create(
                mahopdong=mahopdong,
                loaihopdong=loaihopdong,
                ngaybatdau=ngaybatdau,
                ngayketthuc=ngayketthuc if ngayketthuc else None,
                ghichu=ghichu
            )
            
            messages.success(request, f'Thêm hợp đồng {mahopdong} thành công!')
            return redirect('danh_sach_hop_dong')
            
        except Exception as e:
            messages.error(request, f'Lỗi khi thêm hợp đồng: {e}')
    
    context = {
        'is_adding': True
    }
    return render(request, 'nhanvien/hop_dong_form.html', context)

@login_required(login_url='login')
def chinh_sua_hop_dong(request, mahopdong):
    """Chỉnh sửa hợp đồng"""
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin':
        return redirect('danh_sach_hop_dong')
    
    hop_dong = get_object_or_404(HopDong, mahopdong=mahopdong)
    
    if request.method == 'POST':
        try:
            hop_dong.loaihopdong = request.POST.get('loaihopdong')
            hop_dong.ngaybatdau = request.POST.get('ngaybatdau')
            
            ngayketthuc = request.POST.get('ngayketthuc')
            hop_dong.ngayketthuc = ngayketthuc if ngayketthuc else None
            
            hop_dong.ghichu = request.POST.get('ghichu')
            
            # Validation ngày
            if hop_dong.ngayketthuc and hop_dong.ngaybatdau:
                if hop_dong.ngayketthuc <= hop_dong.ngaybatdau:
                    messages.error(request, 'Ngày kết thúc phải sau ngày bắt đầu.')
                    return render(request, 'nhanvien/hop_dong_form.html', {'hop_dong': hop_dong, 'is_adding': False})
            
            hop_dong.save()
            messages.success(request, f'Cập nhật hợp đồng {mahopdong} thành công!')
            return redirect('chi_tiet_hop_dong', mahopdong=mahopdong)
            
        except Exception as e:
            messages.error(request, f'Lỗi khi cập nhật hợp đồng: {e}')
    
    context = {
        'hop_dong': hop_dong,
        'is_adding': False
    }
    return render(request, 'nhanvien/hop_dong_form.html', context)

@login_required(login_url='login')
def xoa_hop_dong(request, mahopdong):
    """Xóa hợp đồng (chỉ nếu không có nhân viên nào sử dụng)"""
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin':
        messages.error(request, 'Bạn không có quyền xóa hợp đồng.')
        return redirect('danh_sach_hop_dong')
    
    try:
        hop_dong = get_object_or_404(HopDong, mahopdong=mahopdong)
        
        # Kiểm tra có nhân viên nào đang sử dụng hợp đồng này không
        nhan_vien_count = NhanVien.objects.filter(mahopdong=hop_dong).count()
        
        if nhan_vien_count > 0:
            messages.error(request, f'Không thể xóa hợp đồng {mahopdong} vì có {nhan_vien_count} nhân viên đang sử dụng.')
        else:
            hop_dong.delete()
            messages.success(request, f'Đã xóa hợp đồng {mahopdong} thành công.')
            
    except Exception as e:
        messages.error(request, f'Lỗi khi xóa hợp đồng: {e}')
    
    return redirect('danh_sach_hop_dong')

@login_required(login_url='login')
def gia_han_hop_dong(request, mahopdong):
    """Gia hạn hợp đồng"""
    vaitro = get_user_vaitro(request.user)
    if vaitro != 'Admin':
        return redirect('danh_sach_hop_dong')
    
    hop_dong = get_object_or_404(HopDong, mahopdong=mahopdong)
    
    if request.method == 'POST':
        try:
            ngay_ket_thuc_moi = request.POST.get('ngay_ket_thuc_moi')
            ly_do_gia_han = request.POST.get('ly_do_gia_han')
            
            if ngay_ket_thuc_moi:
                ngay_moi = datetime.datetime.strptime(ngay_ket_thuc_moi, '%Y-%m-%d').date()
                
                # Kiểm tra ngày gia hạn phải sau ngày hiện tại
                if ngay_moi <= datetime.date.today():
                    messages.error(request, 'Ngày gia hạn phải sau ngày hiện tại.')
                    return render(request, 'nhanvien/gia_han_hop_dong.html', {'hop_dong': hop_dong})
                
                # Cập nhật hợp đồng
                hop_dong.ngayketthuc = ngay_moi
                hop_dong.ghichu = f"{hop_dong.ghichu or ''}\n[Gia hạn {datetime.date.today()}]: {ly_do_gia_han}".strip()
                hop_dong.save()
                
                messages.success(request, f'Gia hạn hợp đồng {mahopdong} đến {ngay_moi} thành công!')
                return redirect('chi_tiet_hop_dong', mahopdong=mahopdong)
            else:
                messages.error(request, 'Vui lòng chọn ngày gia hạn.')
                
        except Exception as e:
            messages.error(request, f'Lỗi khi gia hạn hợp đồng: {e}')
    
    context = {
        'hop_dong': hop_dong
    }
    return render(request, 'nhanvien/gia_han_hop_dong.html', context)