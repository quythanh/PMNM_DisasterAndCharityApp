"""
Django settings for CharityProject project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vksiqy_8642*=sogpct@mplnexj#g)_u)0$!2oej6&0tggh_j('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'CharityApp',
    'oauth2_provider',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'CharityProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8080",
#     "http://192.168.0.104:8000",
#     "http://127.0.0.1:8080"
# ]
CORS_ALLOW_ALL_ORIGINS = True
WSGI_APPLICATION = 'CharityProject.wsgi.application'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '2ff9-27-64-68-99.ngrok-free.app']

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Oauth2 Secret sqlite3: 4QEmfQijtK5DTREwCg0W4gQcqxww0wIFXSUqvDzsAyuMMPHs6r0x6ydFG2kgcEPehCQmtqq0jD4sWn3rkLHouIkrCte05RBqfm7gsm1VGRszTh5qJBosGvzYfwxfpf4L
# Oauth2 ID: 634POpM5S6PTDpZRgsCHG2cfnvRDgnyCH7c5sF0n
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'charity_db',
    #     'USER': 'root',
    #     'PASSWORD': 'PandaPhat2003@',
    #     'HOST': 'localhost',
    #     'PORT': '3306',
    # }
}

AUTH_USER_MODEL = "CharityApp.User"
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
JAZZMIN_SETTINGS = {
    "site_title": "Hệ thống cứu trợ",
    "site_header": "Quản lý từ thiện và thiên tai",
    "site_brand": "Quản lý chi tiết",
    "welcome_sign": "Chào mừng bạn đến với trang quản lý",
    "copyright": "Copyright © 2024 Quản lý từ thiện và thiên tai",

    # Tùy chỉnh thanh menu bên trái
    "topmenu_links": [
        {"name": "Trang chủ", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "auth"},  # Link đến trang quản lý người dùng
        {"app": "busmap"},  # Link đến trang quản lý ứng dụng busmap
    ],

    # Tùy chỉnh thanh sidebar menu
    "usermenu_links": [
        {"name": "Xem hồ sơ", "url": "admin:auth_user_change", "new_window": False},
    ],

    # Màu sắc chủ đạo của giao diện
    "show_sidebar": True,  # Hiển thị sidebar
    "navigation_expanded": False,  # Không mở rộng menu sidebar mặc định
    "hide_apps": [],  # Ẩn những ứng dụng không cần thiết (nếu có)
    "hide_models": [],  # Ẩn các model không cần thiết trong admin

    # Đăng ký các ứng dụng (apps) và mô hình (models) vào admin
    "icons": {
        "auth": "fas fa-users-cog",  # Ứng dụng auth
        "auth.user": "fas fa-user",  # Model User trong auth
        "auth.Group": "fas fa-users",  # Model Group trong auth

        # Đăng ký các icon cho app busmap và các model của bạn
        "busmap.TuyenDuong": "fas fa-road",  # Icon cho model TuyenDuong
        "busmap.TramDung": "fas fa-bus",  # Icon cho model TramDung
        "busmap.ChuyenXe": "fas fa-shuttle-van",  # Icon cho model ChuyenXe
        "busmap.DanhGiaTuyenDuong": "fas fa-star",  # Icon cho model DanhGiaTuyenDuong
        "busmap.BaoCaoChuyenXe": "fas fa-exclamation-circle",  # Icon cho model BaoCaoChuyenXe
        "busmap.LichTrinh": "fas fa-clock",  # Icon cho model LichTrinh
        "busmap.ViTriXe": "fas fa-map-marker-alt",  # Icon cho model ViTriXe
        "busmap.LichTrinhYeuThich": "fas fa-heart",  # Icon cho model LichTrinhYeuThich
        "busmap.Xe": "fas fa-bus-alt",  # Icon cho model Xe
        "busmap.TuyenTram": "fas fa-random",  # Icon cho model TuyenTram
        "busmap.User": "fas fa-user-tie",  # Icon cho model User
    },

    # Các tùy chọn khác
    "order_with_respect_to": ["auth", "busmap"],  # Đặt thứ tự hiển thị các apps
    "custom_css": None,  # Thêm CSS tùy chỉnh (nếu có)
    "custom_js": None,  # Thêm JavaScript tùy chỉnh (nếu có)
    "show_ui_builder": False,  # Ẩn tính năng "UI Builder"
}
CLOUDINARY = {
    'cloud_name': 'dzm6ikgbo',
    'api_key': '539987548171822',
    'api_secret': 'FfePKpjetbSwFufRAnuWoDMeaIA',
    # 'api_proxy': 'http://proxy.server:3128'
}

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    )
}