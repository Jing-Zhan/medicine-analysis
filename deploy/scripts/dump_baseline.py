#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 13 个接口的真实返回，输出一份紧凑的基准值摘要。

用途：填充《数据基准值.docx》的结果表。脚本只依赖标准库，CentOS 7 自带的
python3.6.8 可以直接跑。

用法（在 master 上执行）：
    python3 deploy/scripts/dump_baseline.py
    # 或者指定地址
    python3 deploy/scripts/dump_baseline.py http://localhost:83

输出每段格式：
    ### 接口路径   HTTP=200  耗时=2.17s
    字段: A, B, C
    前 10 行: ...
"""
import json
import sys
import time
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:83"

# (接口路径, 中文名, 摘要里要展示的最大行数)
ENDPOINTS = [
    ("/home/overview",  "首页概览指标",           10),
    ("/home/citylevel", "城市等级竞争",           10),
    ("/home/age",       "不同年龄患病比例",       10),
    ("/home/top10",     "销售金额 Top10",         10),
    ("/home/province",  "各省份销售格局",         34),
    ("/disease/union",  "目标适应症与药品关联",   20),
    ("/disease/drug",   "药品关联关系图",          5),
    ("/disease/age",    "适应症年龄分布",         20),
    ("/disease/section", "适应症科室分布",        20),
    ("/drug/cities",    "药品覆盖城市",           10),
    ("/drug/hospital",  "药品覆盖医院等级",       10),
    ("/drug/diseases",  "药品对应适应症",         10),
    ("/drug/section",   "药品科室分布",           10),
]


def fmt(v):
    """把单个值压成短字符串。"""
    if isinstance(v, float):
        # 大额金额保留 2 位，比例类保留 2 位
        return ("%.2f" % v).rstrip("0").rstrip(".") if v == int(v) else "%.2f" % v
    if isinstance(v, int):
        return str(v)
    return str(v)


def summarize(obj, max_rows):
    """返回 (字段列表, 行摘要列表)。"""
    fields, lines = [], []

    if isinstance(obj, list):
        if not obj:
            return [], ["（空数组）"]
        if isinstance(obj[0], dict):
            fields = list(obj[0].keys())
            for row in obj[:max_rows]:
                lines.append("  " + " | ".join(fmt(row.get(f, "")) for f in fields))
            if len(obj) > max_rows:
                lines.append("  …共 %d 行" % len(obj))
        else:
            lines.append("  " + ", ".join(fmt(x) for x in obj[:max_rows]))
        return fields, lines

    if isinstance(obj, dict):
        fields = list(obj.keys())
        for k, v in obj.items():
            if isinstance(v, list):
                if v and isinstance(v[0], dict):
                    sub = list(v[0].keys())
                    lines.append("  %s: %d 行, 字段 %s" % (k, len(v), ",".join(sub)))
                    for row in v[:max_rows]:
                        lines.append("    " + " | ".join(fmt(row.get(f, "")) for f in sub))
                    if len(v) > max_rows:
                        lines.append("    …共 %d 行" % len(v))
                else:
                    lines.append("  %s: %s" % (k, ", ".join(fmt(x) for x in v[:max_rows])) +
                                 ("  …共 %d 项" % len(v) if len(v) > max_rows else ""))
            elif isinstance(v, dict):
                lines.append("  %s: {%s}" % (k, ", ".join(v.keys())))
            else:
                lines.append("  %s = %s" % (k, fmt(v)))
        return fields, lines

    return [], ["  " + fmt(obj)]


def main():
    print("基准值抓取：%s" % BASE)
    print("时间：%s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 78)
    for path, name, max_rows in ENDPOINTS:
        url = BASE + path
        t0 = time.time()
        try:
            with urllib.request.urlopen(url, timeout=300) as resp:
                code = resp.getcode()
                body = resp.read().decode("utf-8", "replace")
        except Exception as exc:                      # noqa: BLE001
            print("\n### %-18s %s" % (path, name))
            print("  请求失败：%s: %s" % (type(exc).__name__, exc))
            continue
        cost = time.time() - t0

        print("\n### %-18s %s" % (path, name))
        print("  HTTP=%s  耗时=%.2fs  字节=%d" % (code, cost, len(body)))
        try:
            payload = json.loads(body)
        except ValueError:
            print("  返回不是合法 JSON，前 200 字符：%s" % body[:200])
            continue

        if isinstance(payload, dict) and "code" in payload:
            print("  code=%s success=%s msg=%s" % (payload.get("code"),
                                                   payload.get("success"),
                                                   payload.get("msg")))
            data = payload.get("data")
        else:
            data = payload

        fields, lines = summarize(data, max_rows)
        if fields:
            print("  字段: %s" % ", ".join(fields))
        for line in lines:
            print(line)
    print("\n" + "=" * 78)
    print("抓取结束")


if __name__ == "__main__":
    main()
