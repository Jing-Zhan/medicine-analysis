# 目标适应症及用药数据分析系统

100 万条真实处方数据的多维统计与可视化。一条大数据链路（HDFS → Hive → Kylin 立方体）加一套业务系统（SpringBoot 13 个接口 + Vue 前端 + Django 大屏），**已全部部署在 U+ 虚拟机并跑通**。

> **组员只需要看第一、二、三节。** 三节以内的操作不会碰坏环境；三节以外的事情先问组长。

---

## 一、当前状态（2026-11-13）

| 部分 | 状态 | 说明 |
| --- | --- | --- |
| Hadoop 集群 | ✅ 运行中 | ZooKeeper / HDFS / YARN / HBase / Hive metastore / Kylin 六个组件 |
| MySQL 明细库 | ✅ 100 万行 | 库 `yiyao`，6 张表，已建 9 个索引 |
| Kylin 立方体 | ✅ READY | Cube `bi_cube`，8 个维度、2 个度量，2.95 GB |
| 后端 13 个接口 | ✅ 全部返回真实数据 | 端口 83 |
| 前端页面 | ✅ 可访问 | 打包进后端 jar，与接口同源 |
| Django 大屏 | ✅ 5 张图 | 端口 8000 |
| 文档 | 需求规格 / 基准值 / 部署 / 数据集 已完成 | 见第七节索引 |

**唯一入口：** <http://192.168.207.179:83/>　（在 Windows 虚拟机的浏览器里打开）

---

## 二、组员怎么用（三步）

### 第 1 步：在虚拟终端启动服务

U+ 平台页面里点开**虚拟终端**（网页终端），登录后执行**一条命令**：

```bash
bash /opt/start-all.sh
```

它会自己判断哪些服务没起来、把缺的拉起来，最后打印一份自检结果和访问地址。**看到末尾 `全部就绪` 就成功了。**

预期输出（节选）：

```
== 1/5 集群：ZooKeeper / HDFS / YARN / HBase / Hive metastore / Kylin ==
  [ OK ] ZooKeeper (2181)
  ...
== 3/5 后端接口（83）==
  [ OK ] /home/overview 返回 200
== 5/5 13 个接口连通性（百万行聚合，逐个跑完约 1~2 分钟）==
  [ OK ] /home/overview        0.61 秒
  ...
全部就绪
  前端 + 接口： http://192.168.207.179:83/
  可视化大屏： http://192.168.207.179:8000/
```

启动要 **1~3 分钟**（集群停机时更久），中途不要按 Ctrl+C。

### 第 2 步：在 Windows 里打开浏览器

远程桌面连到 Windows 虚拟机（`192.168.206.223`），打开浏览器访问：

| 想看什么 | 地址 |
| --- | --- |
| **BI 分析系统（前端 + 接口）** | <http://192.168.207.179:83/> |
| 可视化大屏（Django） | <http://192.168.207.179:8000/> |
| Kylin 控制台（看 Cube） | <http://192.168.207.179:7070/kylin>　账号 `ADMIN` / `KYLIN` |
| YARN 任务页 | <http://192.168.207.179:8088/> |
| HDFS 文件页 | <http://192.168.207.179:50070/> |
| HBase 状态页 | <http://192.168.207.179:16010/> |

**打开后如果图表空白或没数据，先按 `Ctrl + F5` 强制刷新**（浏览器缓存了旧页面），再不行跑第三步的检查命令。

### 第 3 步：只是想知道「现在好不好」

```bash
bash /opt/env-status.sh
```

几秒出结果，**只检查不启动任何进程**，适合随时确认环境状态。

---

## 三、四条铁律（不要碰环境）

我们这套环境有 **8 个以上组件、有启动顺序依赖**（ZooKeeper → HDFS → YARN → HBase → Hive → Kylin → 后端 → 大屏）。手工启停极容易顺序错、残留进程占端口，**排查一次要半小时**。所以：

| ❌ 不要做 | 为什么 | ✅ 应该做 |
| --- | --- | --- |
| 手动敲 `start-dfs.sh`、`start-hbase.sh`、`kylin.sh start` 等 | 顺序错了组件会互相连不上，而且会出现「进程在、端口不通」的假活状态 | 一律用 `bash /opt/start-all.sh` |
| 手动 `pkill java`、`killall` | 会连带杀掉 NameNode / HMaster / ResourceManager，集群直接崩 | 只想重启后端：`pkill -f yiyao-0.0.1-SNAPSHOT.jar` 后重跑 start-all.sh |
| 重启虚拟机 | 所有组件都要重起，Cube 要等 Kylin 恢复 | 非必要不重启；真要重启，起来后跑 `bash /opt/start-all.sh` |
| 在服务器上 `git pull` / `git clone` 覆盖整个仓库 | 会覆盖已编译的 jar，以及大屏 `screen/config/settings.py` 的本地补丁，大屏会起不来 | 要更新代码找组长，由组长按目录同步 |
| 改 `application.properties`、`my.cnf`、`core-site.xml` 等配置 | 牵一发动全身 | 先问组长 |
| 删 `target/`、`/var/lib/mysql`、`/bi_data`、HDFS 上的目录 | 数据没了要重新导入 100 万行 | 空间不足找组长 |
| 重跑 `loadData.sh` 导入数据 | 会重复插入，行数变 200 万，所有指标失真 | 需要重导先问组长 |

**改代码的正确流程：** 在自己分支上改 → 推到 GitHub → 告诉组长 → 组长合并到 `main` 后统一构建部署。不要在服务器上直接改源码。

---

## 四、这套系统是什么

```
原始 txt（6 个文件，约 240MB）
  │
  ├─► MySQL yiyao（明细库，100 万行）──► SpringBoot 13 接口 ──► Vue 前端（83 端口，同源）
  │                                    └─► Django 大屏（8000 端口，PyMySQL 直连）
  │
  └─► HDFS ──► Hive 外部表 ──► Kylin Cube bi_cube（8 个维度、2 个度量，READY，2.95 GB）
                                    └─► 预计算链路验证；业务查询经 query.engine 配置切换
```

### 技术栈（实际部署版本）

Hadoop 2.7.3 · Hive 1.2.1 · HBase 1.2.1 · ZooKeeper 3.4.6 · Kylin 3.1.1 · MySQL 5.7.28 ·
SpringBoot 2.5.1 + MyBatis-Plus 3.4.3 · Vue 2 + webpack 3 · Django 3.2.25 + PyMySQL 1.0.2 · CentOS 7 · Python 3.6.8

### 机器

| 节点 | IP | 角色 |
| --- | --- | --- |
| master | 192.168.207.179 | NameNode、ResourceManager、HMaster、Hive metastore、Kylin、MySQL、后端、大屏 |
| slave1 | 192.168.203.160 | DataNode、NodeManager、HRegionServer、ZooKeeper |
| slave2 | 192.168.202.0 | DataNode、NodeManager、HRegionServer、ZooKeeper |
| Windows 跳板 | 192.168.206.223 | 只用来开浏览器看页面，不跑任何服务 |

### 13 个接口与 5 张大屏图

| 接口 | 说明 | 接口 | 说明 |
| --- | --- | --- | --- |
| `/home/overview` | 首页 6 个概览指标 | `/drug/cities` | 城市用药分布（267 城） |
| `/home/citylevel` | 城市等级竞争 | `/drug/hospital` | 药品 × 医院等级 |
| `/home/age` | 年龄患病比例 | `/drug/diseases` | 药品对应适应症 |
| `/home/top10` | 销售金额 Top10 | `/drug/section` | 药品 × 科室 |
| `/home/province` | 各省份销售格局（31 省） | `/disease/union` | 适应症与药品关联 |
| `/disease/drug` | 药品关联关系图 | `/disease/age` | 适应症年龄分布 |
| `/disease/section` | 适应症科室分布 | | |

大屏 5 张图：省份地图、用药数量 Top10、用药金额 Top10 占比、病症出现次数 Top10、药物关联关系。

---

## 五、预期表现（免得以为坏了）

- **明细关联类接口要 5~16 秒**，`/home/overview` 约 0.6 秒。百万行表上做多表关联就是这个量级，不是卡死。首屏 5 张图并行加载，最慢一张约 12~16 秒出图。
- **城市等级图只有一根柱子**：数据只覆盖 2008 年 12 月一个月，时间维度只有一个值 `200812`。
- **年龄分布图男女两根柱几乎等高**：数据里性别接近 1:1 且与年龄无关，各年龄段真实差异只有 0.04 个百分点。
- **概览「处方总数」是 100 万，各分布图加起来是 998,836**：有 1,164 行的 `hosp_id` 在维表里找不到，被 INNER JOIN 过滤。
- **`/disease/section`、`/home/province`、`/drug/cities` 没有排序**：SQL 里没有 ORDER BY，返回顺序不保证，前端图表自己做排序。

这些都属于数据的客观情况，已写进 [数据基准值](docs/数据基准值.docx) 与 [数据集说明](docs/数据集说明.md)。

---

## 六、常见问题

| 现象 | 处理 |
| --- | --- |
| 浏览器打不开 `:83` | 终端跑 `bash /opt/env-status.sh` 看 83 是否在监听；不在就 `bash /opt/start-all.sh` |
| 页面能开但图表全空 | 先 `Ctrl + F5`；仍空就跑 `bash /opt/env-status.sh` 看后端接口是否 200 |
| 页面显示的是假数据（年份 2016-2021、Top10 是 96/88/81） | 说明前端请求失败走了兜底。看 `/tmp/yiyao.log` 末尾报错 |
| 大屏显示「演示数据」角标 | 大屏接口返回 `source` 为 `demo`，说明查库失败。跑 `bash /opt/env-status.sh` 看 `db: true` |
| Kylin 页面打不开 / Cube 列表空 | 集群没起或 Kylin 没起，跑 `bash /opt/start-all.sh` |
| `/opt/start-all.sh` 报某组件 FAIL | 看 `/tmp/start-cluster.log`；后端看 `/tmp/yiyao.log`，大屏看 `/tmp/screen.log` |
| 终端里中文变乱码 | 只是显示问题，不影响功能。文件本身都是 UTF-8 |

**不要自己 `yum install`、`pip install`、`npm install`**——服务器是离线环境，装不上还会留下半装状态。

---

## 七、文档索引

| 文档 | 内容 |
| --- | --- |
| [部署与验收说明](docs/部署与验收说明.md) | 集群启动、MySQL 三项准备、后端双引擎、前端同源部署、验收清单、故障记录、性能实测 |
| [需求规格说明书](docs/需求规格说明书.docx) | 13 个接口 + 5 张大屏图的功能、字段、验收标准 |
| [数据基准值](docs/数据基准值.docx) | 13 个接口的真实数值，验收时逐项对照 |
| [数据集说明](docs/数据集说明.md) | 数据来源、导入方式、以及数据本身的 5 个特征（单月/年龄均匀/性别 1:1/1164 行缺维表/回车符） |
| [环境架构说明](docs/环境架构说明.md) | 组件关系、端口、一句话比喻版全景 |
| [任务看板](docs/任务看板.md) | T1–T24 任务与完成状态 |
| [T7-前端跑通与打包说明](docs/T7-前端跑通与打包说明.md) | 前端改动、13 组件走查、打包方法 |
| [功能测试用例](目标适应症及用药数据分析系统_功能测试用例.docx) | 18 条用例（接口 13 + 大屏 5），已按实测填写结果 |
| [答辩 PPT 提纲](目标适应症及用药数据分析系统_答辩PPT提纲.docx) | 14 页逐页要点与口述稿 |

---

## 八、目录结构

```
medicine-analysis/
├── backend/yiyao/                      后端 SpringBoot（端口 83，同时提供前端静态页面）
│   └── src/main/resources/static/      前端打包产物（由 dist 复制而来，勿手改）
├── frontend/bigdataInCase-Medicine/    前端 Vue2 工程（dev 端口 8083，仅开发用）
├── screen/                             Django 大屏工程（端口 8000）
├── deploy/
│   ├── scripts/start-all.sh            一键启动 + 自检（服务器上装在 /opt/start-all.sh）
│   ├── scripts/env-status.sh           只读状态检查（/opt/env-status.sh）
│   ├── scripts/cube_info.py            打印 Cube 真实维度/度量（/opt/cube_info.py）
│   ├── scripts/dump_baseline.py        抓 13 接口基准值（/opt/dump_baseline.py）
│   └── sql/                            索引、回车符清洗、列宽收窄三个脚本
└── docs/                               全部文档
```

服务器上的实际目录是 `/home/medicine-analysis`，**不是**从这个 git 仓库直接 clone 的，代码由组长按目录同步。

---

## 九、开发约定

### 分支

一人一分支，只在自己的分支上提交，`main` 只有组长合并。

| 分支 | 谁 | 放什么 |
| --- | --- | --- |
| `main` | 组长 | 可运行、可演示的版本 |
| `feature/A-deploy` | 占竞 | 部署脚本、后端、环境文档 |
| `feature/B-screen` | 李艺淼 | Django 大屏 |
| `feature/C-frontend` | 付悌安 | 前端工程 |
| `feature/D-docs` | 杨博文 | 需求规格、可行性、基准值 |
| `feature/E-test` | 洪嘉伟 | 测试用例、答辩材料 |

```bash
git checkout feature/你的分支
git pull origin main        # 每次开工前先拉主干
# ...干活...
git add -A && git commit -m "T7-frontend-build" && git push
```

### 提交信息

`T编号-模块-动作`，例如 `T6-backend-kylin-config`、`T8-screen-province-map`。

### 不要提交

`node_modules/`、`dist/`、`target/`、数据文件（约 600MB）、`docs/_原始版本/`。已在 `.gitignore` 排除，不要 `git add -f` 强加。

### 前端打包（如果确实要改前端）

工程是 webpack 3，**不需要装 Node 14**，Node 24 加一个参数即可：

```bash
cd frontend/bigdataInCase-Medicine
npm install --ignore-scripts --no-audit --no-fund
NODE_OPTIONS=--openssl-legacy-provider npm run build
```

然后把 `dist/*` 复制到 `backend/yiyao/src/main/resources/static/`，重新打包后端。前端是**同源部署**（`src/config.js` 里 `baseUrl: ''`），不要改成绝对地址，否则会跨域。

---

## 十、团队

| 成员 | 角色 | 负责任务 |
| --- | --- | --- |
| 占竞 | 组长 / 环境 + 后端 + 部署 | T1 T2 T5 T6 T9 |
| 李艺淼 | 数据仓库 / 大屏 | T3 T8 |
| 付悌安 | 数据导入 / 前端 | T4 T7 |
| 杨博文 | 文档 / 数据核对 | T10 T11 |
| 洪嘉伟 | 测试 / 答辩材料 | T12 |

任务详情见 [任务看板](docs/任务看板.md)。
