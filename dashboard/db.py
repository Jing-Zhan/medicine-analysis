"""MySQL 连接（PyMySQL 直连，不依赖 mysqlclient 编译）。

连接参数全部来自环境变量，默认值对应实训环境：
    MYSQL_HOST=127.0.0.1
    MYSQL_PORT=3306
    MYSQL_USER=root
    MYSQL_PASSWORD=123456
    MYSQL_DB=yiyao
"""
import os

import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "123456"),
    "database": os.environ.get("MYSQL_DB", "yiyao"),
    "charset": "utf8mb4",
}


def query(sql, args=None):
    """执行一条 SELECT，返回 list[dict]。"""
    conn = pymysql.connect(
        **DB_CONFIG,
        cursorclass=DictCursor,
        connect_timeout=5,
        read_timeout=120,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args or ())
            return list(cur.fetchall())
    finally:
        conn.close()


def ping():
    """启动自检用：返回 True/False。"""
    try:
        query("SELECT 1 AS ok")
        return True
    except Exception:
        return False
