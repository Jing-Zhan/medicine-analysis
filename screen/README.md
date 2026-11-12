# 可视化大屏（Django + ECharts）

5 张图：省份病例数与用药金额地图、用药 TOP10、用药金额分布 TOP10、病症 TOP10、药物关联关系。

工程已完成并可运行。数据**直连 MySQL 的 `yiyao` 库**，不经过 Kylin —— 与 `backend/` 里那套 12 图的 SpringBoot 系统是两条独立链路。

## 目录结构

```
screen/
├── manage.py                    入口
├── requirements.txt             Django + PyMySQL
├── start_local.bat              Windows 一键启动
├── config/                      项目配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/                   业务应用
│   ├── db.py                    PyMySQL 连接
│   ├── queries.py               5 张图的 SQL
│   ├── demo.py                  连不上库时的演示数据
│   ├── views.py                 接口
│   └── urls.py
├── templates/
│   ├── index.html               老师下发的原模板（参考）
│   ├── 地图对照模板.html          地图配置参考
│   └── dashboard/index.html     实际渲染页面
├── static/
│   ├── css/  img/               下发素材
│   ├── js/                      echarts.min.js、china.js、screen.js（自写）
│   └── data/rules_data.csv      关联规则（任务24 产物）
└── 省份对应.xlsx                 省份全称→简称对照
```

## 快速启动

### Windows 本机

```bat
cd screen
python -m pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

或直接双击 `start_local.bat`。

### 虚拟机 CentOS 7

```bash
conda create -n screen python=3.9 -y && conda activate screen
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
python manage.py runserver 0.0.0.0:8000
# 放行端口
firewall-cmd --add-port=8000/tcp --permanent && firewall-cmd --reload
```

浏览器打开 `http://<服务器IP>:8000/`。

### 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MYSQL_HOST` | 127.0.0.1 | MySQL 地址（虚拟机里改成 master 的 IP） |
| `MYSQL_PORT` | 3306 | |
| `MYSQL_USER` | root | |
| `MYSQL_PASSWORD` | 123456 | |
| `MYSQL_DB` | yiyao | |
| `RULES_CSV` | static/data/rules_data.csv | 关联规则文件 |
| `CACHE_TTL` | 60 | 接口缓存秒数，0 表示不缓存 |
| `DJANGO_DEBUG` | 1 | 生产可设 0 |

连不上数据库时不会白屏：接口自动返回 `demo.py` 的演示数据，页面右上角标「演示数据」。

## 接口清单

所有接口均为 `GET`，返回 JSON，且都带一个 `source` 字段：`db` 表示真实查库，`demo` 表示降级数据。

| 接口 | 参数 | 返回字段 | 对应图表 |
| --- | --- | --- | --- |
| `/` | — | HTML 页面 | 大屏整体 |
| `/api/health/` | — | `db`、`rules_csv`、`rules_exists` | 自检 |
| `/api/overview/` | — | `total_rows`、`total_amount`、`prescriptions`、`hosps`、`drugs` | 顶部指标 |
| `/api/province/` | — | `data[]: name`、`short`、`cases`、`amount` | 省份地图 |
| `/api/drug-top10/` | `metric=cases`（默认）/ `amount` | `data[]: name`、`value` | 用药 TOP10 |
| `/api/drug-amount/` | — | `data[]: name`、`value` | 用药金额分布 TOP10 |
| `/api/disease-top10/` | — | `data[]: name`、`value` | 病症 TOP10 |
| `/api/relations/` | — | `nodes[]`、`links[]`（`source`、`target`、`confidence`、`lift`）、`total_rules` | 药物关联 |

### 返回示例

`GET /api/province/`

```json
{
  "data": [
    { "name": "广东省", "short": "广东", "cases": 128640, "amount": 4978368.0 },
    { "name": "北京市", "short": "北京", "cases": 54817,  "amount": 2121987.9 }
  ],
  "source": "db"
}
```

`GET /api/drug-top10/`

```json
{
  "data": [
    { "name": "阿司匹林肠溶片", "value": 38217 },
    { "name": "氯化钠注射液",   "value": 35402 }
  ],
  "source": "db"
}
```

`GET /api/relations/`

```json
{
  "nodes": [ { "name": "阿司匹林", "value": 4 } ],
  "links": [ { "source": "阿司匹林", "target": "氯吡格雷", "confidence": 0.82, "lift": 3.14 } ],
  "total_rules": 50,
  "source": "db"
}
```

### 自测

```bash
curl http://127.0.0.1:8000/api/health/
curl http://127.0.0.1:8000/api/province/
```

`health` 里 `db` 为 `true` 说明数据库通了。

## 五张图与取数逻辑

| 图 | 接口 | 取数要点 |
| --- | --- | --- |
| 省份病例数与用药金额 | `/api/province/` | 先按 `hosp_id` 聚合事实表，再 join `t_view_areas` 取 `province_name` |
| 用药 TOP10 | `/api/drug-top10/` | 按 `SUBSTRING_INDEX(m_drug,'_',1)` 分组计数，取前 10，再回查 `t_view_drug` 名称 |
| 用药金额分布 TOP10 | `/api/drug-amount/` | 同上，度量换成 `SUM(amount)` |
| 病症出现次数 TOP10 | `/api/disease-top10/` | 按 `m_diagnostic1` 分组，join `t_view_disease.disease_type13` 取名称 |
| 药物关联关系 | `/api/relations/` | 不查库，读 `static/data/rules_data.csv`（Apriori 结果），解析 `frozenset({...})` |

## 三个必须注意的坑

1. **`m_drug` 带后缀**：明细里是 `DM0000178036_2`，维表里是 `DM0000178036`，必须 `SUBSTRING_INDEX(m_drug,'_',1)` 才能关联。
2. **省份名称不一致**：库里是「北京市」，`china.js` 只认「北京」，接口同时返回 `name`（全称）和 `short`（简称），地图用 `short`。
3. **空值写成 `-`**：维表普遍用 `-` 表示缺失，用 `NULLIF(x,'-')` 转 NULL 再 `COALESCE`。

## 与 12 图系统的区别

| | 大屏（本目录） | 12 图系统（backend/ + frontend/） |
| --- | --- | --- |
| 技术栈 | Python + Django + ECharts | Vue2 + SpringBoot + MyBatis |
| 图表数 | 5 | 12 |
| 数据源 | **MySQL 直连** | **Kylin**（JDBC 7070） |
| 端口 | 8000 | 83（后端）/ 8080（前端） |

两者互不调用，只是共用同一份 `yiyao` 数据。

## 常见问题

- **页面能开但图空白**：F12 看 Console，多为 `/api/*` 或 `china.js` 404。
- **地图有图不上色**：`short` 字段没对上，打印 `/api/province/` 检查是不是「北京/内蒙古/广西」这种简称。
- **接口 500**：看 runserver 终端日志；或访问 `/api/health/` 看 `db` 是否为 `true`。
- **改了数据看不到**：接口有 60 秒缓存，重启服务或设 `CACHE_TTL=0`。