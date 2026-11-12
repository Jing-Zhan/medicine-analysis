"""5 张大屏图表所需的取数逻辑。

数据表（yiyao 库）：
    prescription_diseases  上报信息表（事实表，约 100 万行）
    t_view_areas           区域表（hosp_id -> province_name / city_level_name ...）
    t_view_drug            药品表（drug -> drug_generic_name ...）
    t_view_disease         疾病表（disease_type13 -> disease_type_name13 ...）
    t_view_hosp            医院表
    t_view_section         科室表

几个坑，这里都处理了：
1. 明细表的 m_drug 形如 "DM0000178036_2"，维表 t_view_drug.drug 是 "DM0000178036"，
   关联时要 SUBSTRING_INDEX(m_drug, '_', 1)。
2. 维表里空值常写成 '-'，用 NULLIF 转成 NULL 再 COALESCE。
3. 直接 100 万行 JOIN 维表很慢，所以统一"先在明细表里聚合，再关联维表"。
"""
import csv
import os
from pathlib import Path

from django.conf import settings

from .db import query

# ---------------------------------------------------------------- 省份名称归一
# 素材包里的 china.js 注册的地图用的是【简称】（北京 / 内蒙古 / 广西 ...），
# 而库里 t_view_areas.province_name 是【全称】（北京市 / 内蒙古自治区 ...），
# 不对齐的话地图上不会有任何颜色。对应关系来自素材包的《省份对应.xlsx》。
_SHORT = {
    "北京市": "北京", "天津市": "天津", "上海市": "上海", "重庆市": "重庆",
    "河北省": "河北", "山西省": "山西", "辽宁省": "辽宁", "吉林省": "吉林",
    "黑龙江省": "黑龙江", "江苏省": "江苏", "浙江省": "浙江", "安徽省": "安徽",
    "福建省": "福建", "江西省": "江西", "山东省": "山东", "河南省": "河南",
    "湖北省": "湖北", "湖南省": "湖南", "广东省": "广东", "海南省": "海南",
    "四川省": "四川", "贵州省": "贵州", "云南省": "云南", "陕西省": "陕西",
    "甘肃省": "甘肃", "青海省": "青海", "台湾省": "台湾",
    "内蒙古自治区": "内蒙古", "广西壮族自治区": "广西", "西藏自治区": "西藏",
    "宁夏回族自治区": "宁夏", "新疆维吾尔自治区": "新疆",
    "香港特别行政区": "香港", "澳门特别行政区": "澳门",
}


def to_short(name):
    """全称 -> china.js 使用的简称。"""
    n = str(name or "").strip()
    if not n:
        return "未知"
    if n in _SHORT:
        return _SHORT[n]
    for suffix in ("特别行政区", "维吾尔自治区", "壮族自治区", "回族自治区", "自治区", "省", "市"):
        if n.endswith(suffix):
            return n[: -len(suffix)]
    return n



# ------------------------------------------------------------------ 1. 省份地图
def province_stats():
    rows = query(
        """
        SELECT a.province_name AS name,
               SUM(t.cases)     AS cases,
               SUM(t.amount)    AS amount
        FROM (
            SELECT hosp_id, COUNT(*) AS cases, SUM(amount) AS amount
            FROM prescription_diseases
            WHERE hosp_id IS NOT NULL
            GROUP BY hosp_id
        ) t
        JOIN t_view_areas a ON a.hosp_id = t.hosp_id
        GROUP BY a.province_name
        """
    )
    out = {}
    for r in rows:
        name = str(r["name"] or "未知").strip()
        item = out.setdefault(name, {"name": name, "cases": 0, "amount": 0.0})
        item["cases"] += int(r["cases"] or 0)
        item["amount"] += float(r["amount"] or 0)
    for item in out.values():
        item["amount"] = round(item["amount"], 2)
    return decorate_province(sorted(out.values(), key=lambda x: x["cases"], reverse=True))


def decorate_province(rows):
    """给每条省份数据补一个 short 字段（地图上用简称）。"""
    for r in rows:
        r["short"] = to_short(r["name"])
    return rows


# ------------------------------------------------------------- 2. 用药 TOP10
def drug_top10(metric="cases"):
    """metric = cases（处方数）| amount（销售金额）"""
    agg = "COUNT(*)" if metric == "cases" else "SUM(amount)"
    rows = query(
        f"""
        SELECT SUBSTRING_INDEX(m_drug, '_', 1) AS drug_id, {agg} AS v
        FROM prescription_diseases
        WHERE m_drug IS NOT NULL AND m_drug <> ''
        GROUP BY drug_id
        ORDER BY v DESC
        LIMIT 10
        """
    )
    # 用通用名展示，取不到再退回包装名、最后退回编码
    name_map = {}
    codes = [r["drug_id"] for r in rows]
    if codes:
        placeholders = ",".join(["%s"] * len(codes))
        for r in query(
            f"SELECT drug, drug_generic_name, package_chinese_name FROM t_view_drug WHERE drug IN ({placeholders})",
            codes,
        ):
            name_map[r["drug"]] = (
                _clean_text(r["drug_generic_name"])
                or _clean_text(r["package_chinese_name"])
                or r["drug"]
            )

    items = [
        {"name": name_map.get(r["drug_id"], r["drug_id"]), "value": round(float(r["v"] or 0), 2)}
        for r in rows
    ]
    items.sort(key=lambda x: x["value"], reverse=True)
    return items[:10]


# --------------------------------------------------------------- 3. 病症 TOP10
def disease_top10():
    rows = query(
        """
        SELECT t.code, t.v, d.disease_type_name13
        FROM (
            SELECT m_diagnostic1 AS code, COUNT(*) AS v
            FROM prescription_diseases
            WHERE m_diagnostic1 IS NOT NULL AND m_diagnostic1 <> ''
            GROUP BY m_diagnostic1
            ORDER BY v DESC
            LIMIT 10
        ) t
        LEFT JOIN t_view_disease d ON d.disease_type13 = t.code
        ORDER BY t.v DESC
        """
    )
    return [
        {
            "name": _clean_text(r["disease_type_name13"]) or r["code"],
            "value": int(r["v"] or 0),
        }
        for r in rows
    ]


# ------------------------------------------------------------------ 4. 总览指标
def overview():
    row = query(
        """
        SELECT COUNT(*)              AS total_rows,
               ROUND(SUM(amount), 2) AS total_amount,
               COUNT(DISTINCT hosp_id) AS hosps
        FROM prescription_diseases
        """
    )[0]
    drugs = query(
        """
        SELECT COUNT(*) AS c FROM (
            SELECT SUBSTRING_INDEX(m_drug, '_', 1) AS d
            FROM prescription_diseases
            WHERE m_drug IS NOT NULL AND m_drug <> ''
            GROUP BY d
        ) t
        """
    )[0]["c"]
    prescriptions = query(
        "SELECT COUNT(DISTINCT m_prescription_id) AS c FROM prescription_diseases"
    )[0]["c"]
    return {
        "total_rows": int(row["total_rows"] or 0),
        "total_amount": float(row["total_amount"] or 0),
        "prescriptions": int(prescriptions or 0),
        "hosps": int(row["hosps"] or 0),
        "drugs": int(drugs or 0),
    }


# ------------------------------------------------------- 5. 药物关联（rules_data.csv）
def rules_path():
    p = os.environ.get("RULES_CSV") or str(Path(settings.BASE_DIR) / "static" / "data" / "rules_data.csv")
    return Path(p)


def _clean_rule_item(text):
    """把 mlxtend 的 frozenset({'阿司匹林'}) 还原成 阿司匹林。"""
    s = str(text or "").strip()
    if s.startswith("frozenset("):
        s = s[len("frozenset("):].rstrip(")")
    s = s.strip("{}[]'\" ").strip()
    return s.split("', '")[0].strip("'\" ")


def _pick(row, *keys):
    for k in keys:
        if k in row:
            return row[k]
    return ""


def relation_graph(limit=40):
    path = rules_path()
    if not path.exists():
        raise FileNotFoundError(f"未找到关联规则文件：{path}")

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    links, degree = [], {}
    for row in rows:
        src = _clean_rule_item(_pick(row, "antecedents", "前项", "antecedent"))
        dst = _clean_rule_item(_pick(row, "consequents", "后项", "consequent"))
        if not src or not dst or src == dst:
            continue
        try:
            conf = float(_pick(row, "confidence", "置信度") or 0)
        except ValueError:
            conf = 0.0
        try:
            lift = float(_pick(row, "lift", "提升度") or 0)
        except ValueError:
            lift = 0.0
        links.append({"source": src, "target": dst, "confidence": round(conf, 4), "lift": round(lift, 3)})
        degree[src] = degree.get(src, 0) + 1
        degree[dst] = degree.get(dst, 0) + 1

    links.sort(key=lambda x: (x["lift"], x["confidence"]), reverse=True)
    links = links[:limit]

    keep = {x for link in links for x in (link["source"], link["target"])}
    nodes = [{"name": n, "value": degree.get(n, 1)} for n in sorted(keep, key=lambda n: degree.get(n, 0), reverse=True)]

    return {"nodes": nodes, "links": links, "total_rules": len(rows)}


def _clean_text(v):
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s in ("-", "\\N", "null", "NULL") else s
