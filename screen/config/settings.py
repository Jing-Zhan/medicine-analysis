"""
Django 閰嶇疆 鈥斺€?鑽搧鍙鍖栧ぇ灞忥紙5 寮犲浘锛?

璁捐瑕佺偣锛?
1. 鏈」鐩笉浣跨敤 Django ORM / 涓嶅缓琛紝MySQL 閲岀殑 6 寮犱笟鍔¤〃鏄閮ㄦ棦鏈夌殑锛?
   鎵€浠?DATABASES 淇濈暀涓€涓?sqlite 鍙槸涓轰簡婊¤冻 Django 鐨勫惎鍔ㄨ姹傘€?
2. 鐪熸鐨勬暟鎹闂蛋 dashboard/db.py 閲岀殑 PyMySQL 鐩磋繛銆?
3. 鎵€鏈夎繛鎺ュ弬鏁伴兘鍙敤鐜鍙橀噺瑕嗙洊锛屾柟渚垮湪铏氭嫙鏈?/ 鏈満涔嬮棿鍒囨崲銆?
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-yiyao-screen-2026")

# 澶у睆閮ㄧ讲鍦ㄨ櫄鎷熸満閲岋紝鐢?IP 璁块棶锛屾墍浠?DEBUG 榛樿寮€銆丠OST 鏀惧紑
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 涓嶄娇鐢?ORM锛岃繖閲屽彧鏄 Django 鑳芥甯稿惎鍔?
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = False

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 鎺ュ彛缁撴灉缂撳瓨绉掓暟锛岄伩鍏嶅ぇ灞忓埛鏂版椂鍙嶅鍘?MySQL锛堣 0 鍙叧闂級
CACHE_TTL = int(os.environ.get("CACHE_TTL", "60"))
