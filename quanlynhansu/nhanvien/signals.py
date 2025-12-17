from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChiTietBangLuong, Luong

@receiver(post_save, sender=ChiTietBangLuong)
def sync_luong_from_chitiet(sender, instance, created, **kwargs):
    """
    Đảm bảo mức Lương Cơ Bản, BHXH, Phụ cấp và Thuế TNCN mới nhất 
    được đồng bộ sang bảng Luong (Thông tin Lương cơ bản).
    """
    
    nv_instance = instance.ma_nhan_vien 
    
    # 1. Kiểm tra bản ghi mới nhất (đảm bảo không ghi đè bằng dữ liệu cũ hơn)
    latest_chitiet = ChiTietBangLuong.objects.filter(ma_nhan_vien=nv_instance).order_by('-thang_luong').first()
    
    if latest_chitiet and latest_chitiet.thang_luong > instance.thang_luong:
         return 

    # Tính tổng phụ cấp để lưu vào cột 'phucap' của bảng Luong
    tong_phu_cap = instance.phu_cap_xang_xe + instance.phu_cap_khac
    
    # 2. Cập nhật hoặc tạo bản ghi Luong (UPSERT)
    luong_instance, created_luong = Luong.objects.update_or_create(
        manhanvien=nv_instance, # Khóa chính là manhanvien
        defaults={
            'luongcoban': instance.luong_co_ban_thuc_lanh,
            'hesoluong': 1.0, # Giữ mặc định 1.0
            'bhxh': instance.trich_bhxh,
            'bhyt': instance.trich_bhyt,
            'bhtn': instance.trich_bhtn,
            'phucap': tong_phu_cap,
            'thuethunhap': instance.thue_tncn # Số tiền thuế TNCN
        }
    )
    # LƯU Ý: Nếu đã dùng update_or_create, không cần gọi .save() sau đó.