"""
Django 配置 —— 药品可视化大屏（5 张图）

设计要点：
1. 本项目不使用 Django ORM / 不建表，MySQL 里的 6 张业务表是外部既有的，
   所以 DATABASES 保留一个 sqlite 只是为了满足 Django 的启动要求。
2. 真正的数据访问走 dashboard/db.py 里的 PyMySQL 直连。
3. 所有连接参数都可用环境变量覆盖，方便在虚拟机 / 本机之间切换。
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-yiyao-screen-2026")

# 大屏部署在虚拟机里，用 IP 访问，所以 DEBUG 默认开、HOST 放开
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

ROOT_URLCONF = "screen.urls"

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

WSGI_APPLICATION = "screen.wsgi.application"

# 不使用 ORM，这里只是让 Django 能正常启动
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

# 接口结果缓存秒数，避免大屏刷新时反复压 MySQL（设 0 可关闭）
CACHE_TTL = int(os.environ.get("CACHE_TTL", "60"))
