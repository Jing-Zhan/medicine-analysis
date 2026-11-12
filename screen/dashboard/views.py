"""大屏页面 + 5 个数据接口。

统一约定：
    成功  -> {"source": "db",   ...业务字段}
    失败  -> {"source": "demo", "error": "...", ...演示数据}
前端根据 source 字段显示「演示数据」角标。
"""
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

from . import demo, queries
from .db import ping

log = logging.getLogger(__name__)

JSON_KW = {"json_dumps_params": {"ensure_ascii": False}}


def index(request):
    return render(request, "dashboard/index.html")


def _wrap(payload, source, error=None):
    # 查询函数可能返回 dict（overview/relations）或 list（省份/TOP10）
    data = dict(payload) if isinstance(payload, dict) else {"data": payload}
    data["source"] = source
    if error:
        data["error"] = error[:300]
    return data


def _cached(request, key, loader, fallback):
    cache_key = "screen:" + key
    data = cache.get(cache_key)
    if data is None:
        try:
            data = _wrap(loader(), "db")
        except Exception as exc:  # 数据库没起来 / 表没导入 / SQL 出错
            log.warning("接口 %s 取数失败，使用演示数据：%s", key, exc)
            data = _wrap(fallback(), "demo", f"{type(exc).__name__}: {exc}")
        cache.set(cache_key, data, getattr(settings, "CACHE_TTL", 60))
    return JsonResponse(data, **JSON_KW)


def overview(request):
    return _cached(request, "overview", queries.overview, demo.overview)


def province(request):
    return _cached(
        request,
        "province",
        queries.province_stats,
        lambda: queries.decorate_province(demo.province()),
    )


def drug_top10(request):
    metric = request.GET.get("metric", "cases")
    if metric == "amount":
        return _cached(request, "drug_amount", lambda: queries.drug_top10("amount"), demo.drug_amount_top10)
    return _cached(request, "drug_cases", lambda: queries.drug_top10("cases"), demo.drug_top10)


def drug_amount(request):
    return _cached(request, "drug_amount", lambda: queries.drug_top10("amount"), demo.drug_amount_top10)


def disease_top10(request):
    return _cached(request, "disease", queries.disease_top10, demo.disease_top10)


def relations(request):
    return _cached(request, "relations", queries.relation_graph, demo.relation_graph)


def health(request):
    return JsonResponse(
        {
            "db": ping(),
            "rules_csv": str(queries.rules_path()),
            "rules_exists": queries.rules_path().exists(),
        },
        **JSON_KW,
    )
