#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印 Kylin Cube 的真实状态、体积、维度与度量。

关于 Kylin 3.1.1 的接口返回结构（踩过两次坑，这里写清楚）：
    /api/cubes?cubeName=...   只返回列表摘要，dimensions 为空
    /api/cube/{name}          Kylin 2.x 的路径，3.1.1 上返回 404
    /api/cubes/{name}         正确路径，返回的是 Cube 实例摘要：
                                - descriptor 只是一个字符串，即 Cube 名称，不是完整描述符
                                - 维度不在返回体里，但每个维度都会生成一个字典，字典键
                                  形如 PRESCRIPTION_DISEASES.AGE，保存在
                                  segments[0].dictionaries 中，可据此还原维度清单
                                - size_kb 是立方体体积，单位为 KB
                                - segments[0].input_records 是构建时读取的记录数

用法（在 master 上）：
    python3 /opt/cube_info.py
    python3 /opt/cube_info.py bi_cube yiyao
"""
import base64
import json
import sys
import urllib.request

CUBE = sys.argv[1] if len(sys.argv) > 1 else "bi_cube"
PROJ = sys.argv[2] if len(sys.argv) > 2 else "yiyao"
BASE = "http://master:7070/kylin"

CANDIDATES = [
    "/api/cubes/%s?projectName=%s" % (CUBE, PROJ),
    "/api/cube/%s?projectName=%s" % (CUBE, PROJ),
    "/api/cubes?cubeName=%s&projectName=%s" % (CUBE, PROJ),
]

_token = base64.b64encode(b"ADMIN:KYLIN").decode()
body = None
for path in CANDIDATES:
    req = urllib.request.Request(BASE + path)
    req.add_header("Authorization", "Basic " + _token)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        break
    except Exception:                                   # noqa: BLE001
        continue

if body is None:
    print("三个候选接口都失败，请打开 Kylin 控制台确认 Cube 名称与项目名")
    sys.exit(1)

if isinstance(body, list):
    body = body[0] if body else {}

segments = body.get("segments") or []
seg = segments[0] if segments else {}

size_kb = float(body.get("size_kb") or seg.get("size_kb") or 0)
gb = size_kb / 1024.0 / 1024.0

print("=" * 66)
print("立方体   %s" % body.get("name", CUBE))
print("状态     %s" % body.get("status", "未知"))
print("体积     %.2f GB" % gb)
print("项目     %s" % (body.get("project") or PROJ))
if seg:
    print("构建段   %s" % seg.get("name", ""))
    print("输入记录 %s 行" % seg.get("input_records", "-"))
    src = seg.get("input_records_size")
    if src:
        print("源数据   %.0f MB" % (float(src) / 1024.0 / 1024.0))
print("=" * 66)

# ---------------------------------------------------------------- 维度
dims = None
desc = body.get("descriptor")
if isinstance(desc, dict):
    dims = desc.get("dimensions")

names = []
if dims:
    for d in dims:
        names.append("%s.%s" % (d.get("table", ""), d.get("name") or d.get("column", "")))
elif seg.get("dictionaries"):
    for key in sorted(seg["dictionaries"]):
        names.append(key)

print("维度     %d 个" % len(names))
for n in names:
    print("         %s" % n)
if names:
    print("         cuboid 数量 2^%d = %d" % (len(names), 2 ** len(names)))

# ---------------------------------------------------------------- 度量
measures = None
if isinstance(desc, dict):
    measures = desc.get("measures")

print("")
if measures:
    print("度量     %d 个" % len(measures))
    for m in measures:
        fn = m.get("function") or {}
        param = fn.get("parameter")
        if isinstance(param, dict):
            param = param.get("value")
        print("         %s  %s(%s)" % (m.get("name", ""), fn.get("expression", ""), param or ""))
else:
    print("度量     接口返回体中不含度量定义")
    print("         建库脚本里显式添加的是 SUM(PRICE) 与 SUM(AMOUNT) 两个")
print("")
