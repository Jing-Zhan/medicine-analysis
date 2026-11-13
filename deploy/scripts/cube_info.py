#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印 Kylin Cube 的真实维度、度量与查找表清单。

注意接口选择：
    /api/cubes?cubeName=...     → 只返回列表摘要，dimensions 为空（踩过的坑）
    /api/cube/{cubeName}        → 返回完整描述，含 dimensions / measures / lookups

用法（在 master 上）：
    python3 cube_info.py                 # 默认 bi_cube / 项目 yiyao
    python3 cube_info.py bi_cube yiyao
"""
import base64
import json
import sys
import urllib.request

CUBE = sys.argv[1] if len(sys.argv) > 1 else "bi_cube"
PROJ = sys.argv[2] if len(sys.argv) > 2 else "yiyao"
BASE = "http://master:7070/kylin"

url = "%s/api/cube/%s?projectName=%s" % (BASE, CUBE, PROJ)
req = urllib.request.Request(url)
token = base64.b64encode(b"ADMIN:KYLIN").decode()
req.add_header("Authorization", "Basic " + token)
req.add_header("Accept", "application/json")

try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
except Exception as exc:                              # noqa: BLE001
    print("请求失败：%s: %s" % (type(exc).__name__, exc))
    print("URL: %s" % url)
    sys.exit(1)

# 兼容两种返回结构：描述符在顶层，或包在 descriptor 里
desc = body.get("descriptor") or body

print("=" * 74)
print("Cube：%s　状态：%s　大小：%.2f GB"
      % (body.get("name", CUBE),
         body.get("status", "?"),
         float(body.get("size_kb", 0)) / 1024.0 / 1024.0))
print("Project：%s　构建引擎：%s"
      % (body.get("project", PROJ), desc.get("engine_type", "?")))
print("=" * 74)


def show_dims():
    dims = desc.get("dimensions") or []
    print("\n--- 维度（%d 个）---" % len(dims))
    for d in dims:
        name = d.get("name", "")
        col = d.get("column") or ""
        tbl = d.get("table") or ""
        if isinstance(col, dict):                     # 派生列
            col = col.get("expression") or json.dumps(col, ensure_ascii=False)[:60]
        print("  %-34s %-16s %s" % (name, tbl, col))
    if dims:
        n = len(dims)
        print("\n  维度组合数 2^%d = %d 个 cuboid" % (n, 2 ** n))


def show_measures():
    ms = desc.get("measures") or []
    print("\n--- 度量（%d 个）---" % len(ms))
    for m in ms:
        fn = m.get("function") or {}
        param = fn.get("parameter")
        if isinstance(param, dict):
            param = param.get("value")
        print("  %-28s %-12s %s"
              % (m.get("name", ""), fn.get("expression", ""), param))


def show_lookups():
    lk = desc.get("lookups") or []
    print("\n--- 查找表（%d 个）---" % len(lk))
    for l in lk:
        print("  表 %-16s 别名 %-16s kind=%s"
              % (l.get("table", ""), l.get("alias", ""), l.get("kind", "LOOKUP")))


show_dims()
show_measures()
show_lookups()

if not (desc.get("dimensions") or desc.get("measures")):
    print("\n顶层键：%s" % ", ".join(body.keys()))
    print("未在预期位置找到 dimensions / measures，原始 JSON 已写入 /tmp/cube_raw.json")
    with open("/tmp/cube_raw.json", "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False, indent=2)
