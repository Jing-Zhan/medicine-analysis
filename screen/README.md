# 可视化大屏（Django）

负责人：成员 B（任务 T8）

## 现状

老师下发了大屏的**静态资源与模板**，没有 Python 代码。Django 工程需要新建。

已放置的内容：

```
screen/
├── static/
│   ├── css/        app.css、bootstrap.min.css
│   ├── js/         echarts.min.js、china.js、d3.min.js、jquery
│   └── img/        背景图、标题栏、panel 等
├── templates/
│   ├── index.html          大屏主页
│   └── 地图对照模板.html     地图配置参考
└── 省份对应.xlsx             省份名称对照
```

## 建工程步骤

```bash
# 1. 在 screen/ 目录下创建 Django 工程，注意用 . 表示当前目录
cd screen
django-admin startproject medicine .

# 2. 创建应用
python manage.py startapp drug_display
```

> 若 `django-admin` 提示找不到，先 `pip install django`

## settings.py 配置

```python
INSTALLED_APPS = [
    # ...
    'drug_display',
]

TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],      # 关键：指向项目自带模板
        # ...
    },
]

STATICFILES_DIRS = [
    BASE_DIR / 'static',                        # 关键：指向项目自带静态资源
]

STATIC_URL = '/static/'

ALLOWED_HOSTS = ["*"]                           # 演示环境，允许所有来源

# 数据库指向 master 的 MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yiyao',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '<master-ip>',
        'PORT': '3306',
    }
}
```

## 视图与路由

```python
# drug_display/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')
```

```python
# medicine/urls.py
from django.urls import path
from drug_display import views

urlpatterns = [
    path('', views.index),
]
```

## 五张图的数据

| 图 | 建议取数 |
| --- | --- |
| 省份病例数与用药金额地图 | 按 `hosp_id` 关联 `t_view_areas`，`group by province_name`，`sum(price)`、`count(*)` |
| 用药 TOP10 | 关联 `t_view_drug`，`group by drug_generic_name`，`order by sum(amount) desc limit 10` |
| 用药分布 TOP10 | 同上，按品种数或金额占比 |
| 病症出现次数 TOP10 | 关联 `t_view_disease`，`group by disease_type13`，`count(*)` |
| 药物关联关系 | Apriori（mlxtend）计算共现，或按处方 ID 做自关联统计 |

> 省份名称要和 `china.js` 匹配：`china.js` 用的是「北京」「广东」这种短名，MySQL 里可能是「北京市」「广东省」。用 `省份对应.xlsx` 或做字符串截断处理。

## 接口与页面分离（推荐）

不建议把数据直接 render 到模板里。推荐形态：

1. `views.py` 提供 `/api/province`、`/api/drugtop10` 等接口，返回 JSON
2. `index.html` 里的 ECharts 通过 Ajax 取数，与原模板的 JS 结构一致

这样改图只动 JS，改数只动视图，互不影响。

## 与后端的区别

后端（SpringBoot）是 Java 服务，端口 83；大屏（Django）是独立的 Python 服务，端口 8000。两者**互不调用**，各自直连 MySQL。
