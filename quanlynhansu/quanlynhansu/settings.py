from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-^lz&i8ky1-i&*+-g)%oq93uz@-9gp-qhk6ea2ywet_ailsun&l'

DEBUG = True

ALLOWED_HOSTS = []

# Ứng dụng
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'nhanvien',  # app quản lý nhân viên
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quanlynhansu.urls'

# ✅ Cấu hình template
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Thêm dòng này để Django nhận templates ngoài app
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'quanlynhansu.wsgi.application'

# ✅ Cấu hình PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'quanlynhansu',  # Tên DB trong pgAdmin
        'USER': 'postgres',
        'PASSWORD': '123',       # Mật khẩu PostgreSQL của bạn
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# ✅ Cấu hình ngôn ngữ và thời gian
LANGUAGE_CODE = 'vi'      # đổi sang tiếng Việt
TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True
USE_TZ = False  # Đặt False nếu muốn dùng giờ VN trực tiếp

# ✅ Cấu hình static (CSS, JS, ảnh)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# ✅ Cấu hình media files (ảnh upload)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ✅ Khóa chính mặc định
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
