"""
# Django 配置 —— 药品可视化大屏（5 张图）

# 设计要点：
# 1. 本项目不使用 Django ORM / 不建表，MySQL 里的 6 张业务表是外部既有的；
#    所以 DATABASES 只保留一个占位后端，仅用于满足 Django 的启动检查。
# 2. 真正的数据访问走 dashboard/db.py 里的 PyMySQL 直连。
# 3. 所有连接参数都可以用环境变量覆盖，方便在虚拟机 / 本机之间切换。
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

# 不使用 ORM，这里只是让 Django 能正常启动
DATABASES = {
    "default": {
        # 系统自带 SQLite 为 3.7.17，低于 Django 3.2 要求的 3.9.0，直接用 sqlite3 后端会启动失败。
        # 本项目不走 ORM（取数全部由 dashboard/db.py 里的 PyMySQL 直连完成），
        # 因此用 dummy 后端占位：Django 能正常启动，误用 ORM 时会明确报错而不是悄悄连错库。
        "ENGINE": "django.db.backends.dummy",
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

# 接口结果缓存秒数，避免大屏刷新时反复查 MySQL（设 0 可关闭）
CACHE_TTL = int(os.environ.get("CACHE_TTL", "60"))
