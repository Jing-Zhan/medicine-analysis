# 目标适应症及用药数据分析系统

医疗处方数据的多维统计与可视化。由两个可运行的系统组成，共用一份数据源。

| 系统 | 技术栈 | 图表 | 入口 |
| --- | --- | --- | --- |
| BI 分析系统 | Vue2 + SpringBoot + MyBatis + Kylin | 12 类 | `http://<master-ip>:8080/dist` |
| 药品可视化大屏 | Python 3.9 + Django + ECharts | 5 类 | `http://<master-ip>:8000` |

## 数据链路

```
MySQL(yiyao) ──► HBase ──► Hive 外部表 ──► Kylin Cube ──► SpringBoot 12 接口 ──► Vue 前端
MySQL(yiyao) ──► Django 视图 ──► ECharts 大屏
```

## 目录结构

```
medicine-analysis/
├── backend/yiyao/                      后端 SpringBoot 工程（端口 83）
├── frontend/bigdataInCase-Medicine/    前端 Vue2 工程（dev 端口 8083）
├── screen/                             可视化大屏 Django 工程
│   ├── static/                         大屏静态资源（模板已提供）
│   ├── templates/                      index.html 与地图对照模板
│   └── 省份对应.xlsx                    地图省份名称对照
├── deploy/
│   ├── start-all.sh                    集群启动脚本
│   └── README.md                       部署与启动说明
└── docs/
    ├── 环境信息卡.md                    服务器地址、账号、端口
    ├── 任务看板.md                      T1—T12 任务与状态
    └── 数据集说明.md                    数据文件位置与导入方式
```

## 快速开始

### 1. 后端

```bash
cd backend/yiyao
# 修改 src/main/resources/application.properties 中的 MySQL 与 Kylin 地址
mvn clean package -DskipTests
java -jar target/yiyao-0.0.1-SNAPSHOT.jar
```

### 2. 前端

```bash
cd frontend/bigdataInCase-Medicine
# 修改 src/config.js 中的 baseUrl 为 http://<master-ip>:83
npm install          # Node 版本需为 14.x
npm run dev          # 本地调试，端口 8083
npm run build        # 产物在 dist/
```

### 3. 大屏

```bash
cd screen
python manage.py runserver 0.0.0.0:8000
```

## 分支约定

**一人一分支。** 只在自己的分支上提交，任何人不直接改 `main`。

| 分支 | 谁用 | 放什么内容 |
| --- | --- | --- |
| `main` | 仅组长合并 | 可运行、可演示的版本 |
| `feature/A-deploy` | 成员 A | 部署脚本、后端配置、环境文档 |
| `feature/B-screen` | 成员 B | Hive 表结构记录、Django 大屏工程 |
| `feature/C-frontend` | 成员 C | MySQL 导入脚本、前端 config 与打包说明 |
| `feature/D-docs` | 成员 D | 需求规格、数据库设计、概要/详细设计 |
| `feature/E-test` | 成员 E | 测试用例、测试报告、答辩材料 |

### 日常流程

```bash
# 1. 切到自己的分支
git checkout feature/C-frontend

# 2. 每次开始干活前，先拉主干最新代码（防止越积越难合）
git pull origin main

# 3. 干活……

# 4. 提交并推送
git add -A
git commit -m "T4-data-loaddata-verify"
git push
```

### 组长合并

每天 21:00 站立会后合并一次。合并前在本地把分支拉下来跑一遍，确认能启动再合：

```bash
git checkout main
git pull
git merge feature/C-frontend --no-ff -m "merge: T4 T7 完成"
git push
```

合并后如果发现问题，用 `git revert` 回退，不要用 `reset` 改写已推送的历史。

### 提交信息格式

`T编号-模块-动作`

```
T4-data-loaddata-verify
T6-backend-kylin-config
T8-screen-province-map
```

### 不要提交这些

`node_modules/`、`dist/`、`target/`、数据文件（约 600MB）、`.idea/`。
已在 `.gitignore` 中排除，不要用 `git add -f` 强行加入。

## 团队

| 成员 | 角色 | 负责任务 |
| --- | --- | --- |
| A | 项目经理 / 集群与 Kylin | T1 T2 T5 T6 T9 |
| B | 数据仓库 / 大屏开发 | T3 T8 |
| C | 数据导入 / 前端工程 | T4 T7 |
| D | 文档 / 数据核对 | T10 T11 |
| E | 测试 / 答辩材料 | T12 |

任务详情见 [docs/任务看板.md](docs/任务看板.md)。

## 注意事项

- 数据文件（约 600MB）不在仓库内，位置见 `docs/数据集说明.md`
- 前端为 webpack 3 + Vue 2 老工程，Node 版本固定 14.16.1，勿用 16 及以上
- 后端端口为 `83`，前端 `config.js` 的 baseUrl 需与之对应
- 集群有启动顺序要求，见 `deploy/README.md`
