# FILE: nhanvien/urls.py (ĐÃ CẬP NHẬT HOÀN CHỈNH)

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards (Dùng name='dashboard' cho Admin/Quản lý)
    path('', views.dashboard_router, name='dashboard_router'),
    path('hrm/dashboard/', views.admin_dashboard, name='dashboard'), 
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'), 
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    
    # Nhân Viên & Tổ Chức
    path('employees/', views.danh_sach_nhan_vien, name='danh_sach_nhan_vien'),
    path('employees/add/', views.them_moi_nhan_vien, name='them_moi_nhan_vien'),
    path('employees/<str:manhanvien>/edit/', views.chinh_sua_nhan_vien, name='chinh_sua_nhan_vien'), 
    path('employees/<str:manhanvien>/', views.chi_tiet_nhan_vien, name='chi_tiet_nhan_vien'),
    path('profile/', views.ho_so_ca_nhan, name='ho_so_ca_nhan'),
    
    # Quản Lý (Admin/Manager)
    path('management/departments/', views.quanly_phong_ban_view, name='quanly_phong_ban'),
    path('management/departments/add/', views.them_phong_ban, name='them_phong_ban'),
    path('management/departments/<str:maphongban>/edit/', views.chinh_sua_phong_ban, name='chinh_sua_phong_ban'),
    path('management/departments/<str:maphongban>/', views.chitiet_phong_ban, name='chitiet_phong_ban'), # Chi tiết PB
    
    # Quản lý Hợp đồng
    path('management/contracts/', views.danh_sach_hop_dong, name='danh_sach_hop_dong'),
    path('management/contracts/add/', views.them_hop_dong, name='them_hop_dong'),
    path('management/contracts/<str:mahopdong>/', views.chi_tiet_hop_dong, name='chi_tiet_hop_dong'),
    path('management/contracts/<str:mahopdong>/edit/', views.chinh_sua_hop_dong, name='chinh_sua_hop_dong'),
    path('management/contracts/<str:mahopdong>/delete/', views.xoa_hop_dong, name='xoa_hop_dong'),
    path('management/contracts/<str:mahopdong>/extend/', views.gia_han_hop_dong, name='gia_han_hop_dong'),
    
    # Lương (Tài Chính)
    path('management/salary/', views.quanly_luong_view, name='quanly_luong'), # Quản lý Lương CB
    path('management/salary/payroll/', views.tinh_luong_payroll, name='tinh_luong_payroll'), # <--- THÊM DÒNG NÀY
    path('management/salary/payslip/<int:payroll_id>/', views.in_phieu_luong, name='in_phieu_luong'),
    path('my-salary/', views.luong_ca_nhan_view, name='luong_ca_nhan'),
    
    # Chuyển khoản lương
    path('management/salary/banking/', views.quan_ly_chuyen_khoan_luong, name='quan_ly_chuyen_khoan_luong'),
    path('management/salary/banking/update-method/', views.cap_nhat_phuong_thuc_tra_luong, name='cap_nhat_phuong_thuc_tra_luong'),
    path('management/salary/banking/transfer/', views.thuc_hien_chuyen_khoan_luong, name='thuc_hien_chuyen_khoan_luong'),
    path('banking/history/', views.lich_su_chuyen_khoan, name='lich_su_chuyen_khoan'),
    
    # QUẢN LÝ KHEN THƯỞNG / KỶ LUẬT
    path('management/rewards/', views.danh_sach_khenthuong_kyluat, name='danh_sach_khenthuong_kyluat'),
    path('management/rewards/add/', views.them_khenthuong_kyluat, name='them_khenthuong_kyluat'),
    path('management/rewards/edit/<int:maktkl>/', views.sua_khenthuong_kyluat, name='sua_khenthuong_kyluat'),
    path('management/rewards/delete/<int:maktkl>/', views.xoa_khenthuong_kyluat, name='xoa_khenthuong_kyluat'),

    # QUẢN LÝ NGHỈ PHÉP
    path('leaves/', views.nghiphep_list, name='nghiphep_list'),
    path('leaves/add/', views.them_nghiphep, name='them_nghiphep'),
    path('leaves/approve/<int:madon>/<str:trangthai_moi>/', views.duyet_nghiphep, name='duyet_nghiphep'),

    # CHẤM CÔNG (CHỈ QUẢN LÝ PHÒNG BAN)
    path('attendance/', views.chamcong_list, name='chamcong_list'),
    path('attendance/action/<str:action>/', views.thuc_hien_cham_cong, name='thuc_hien_cham_cong'),

    # TUYỂN DỤNG
    path('recruitment/', views.tuyendung_list, name='tuyendung_list'),

    # QUẢN LÝ ỨNG VIÊN
    path('recruitment/candidates/', views.danh_sach_ung_vien, name='danh_sach_ung_vien'),
    path('recruitment/candidates/add/', views.them_ung_vien, name='them_ung_vien'),
    path('recruitment/candidates/edit/<str:ma_uv>/', views.sua_ung_vien, name='sua_ung_vien'),
    path('recruitment/candidates/delete/<str:ma_uv>/', views.xoa_ung_vien, name='xoa_ung_vien'),

    # TÍNH NĂNG CHO NHÂN VIÊN (CHỈ XEM)
    path('employee/departments/', views.nhanvien_xem_phong_ban, name='nhanvien_xem_phong_ban'),
    path('employee/colleagues/', views.nhanvien_xem_dong_nghiep, name='nhanvien_xem_dong_nghiep'),
    path('employee/jobs/', views.nhanvien_xem_tuyen_dung, name='nhanvien_xem_tuyen_dung'),
    path('employee/rewards/', views.nhanvien_xem_khen_thuong_ky_luat, name='nhanvien_xem_khen_thuong_ky_luat'),

    # QUẢN LÝ PHÊ DUYỆT TÀI KHOẢN (CHỈ ADMIN)
    path('management/accounts/approval/', views.quan_ly_phe_duyet_tai_khoan, name='quan_ly_phe_duyet_tai_khoan'),
    path('management/accounts/approval/<str:tendangnhap>/<str:action>/', views.phe_duyet_tai_khoan, name='phe_duyet_tai_khoan'),
]