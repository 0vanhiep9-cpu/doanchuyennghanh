# FILE: nhanvien/apps.py

from django.apps import AppConfig

class NhanvienConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nhanvien'
    
    # ĐĂNG KÝ TÍN HIỆU TẠI ĐÂY
    def ready(self):
        # Import file signals.py của ứng dụng nhanvien
        import nhanvien.signals