# BI 分析前端（bigdataInCase-Medicine）

Vue 2 + webpack 3 老工程，负责 3 个页面、13 个图表组件。

## 1. 环境

| 项 | 要求 | 说明 |
| --- | --- | --- |
| Node | **14.16.1** | 版本太高（16/18/20）webpack 3 会编译失败，用 nvm 切换：`nvm install 14.16.1` + `nvm use 14.16.1` |
| npm | 6.x（随 Node 14 安装） | |

```bash
node -v      # 必须是 v14.16.1
npm -v
```

## 2. 安装依赖

```bash
cd frontend/bigdataInCase-Medicine
npm install
```

网络慢或报错时换镜像源：

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

## 3. 接口地址

只改 **`src/config.js`** 一处，其它代码都引用这个变量：

```js
export default {
    baseUrl: 'http://192.168.207.179:83',  // 后端接口地址
    useMock: true,                          // true=用前端假数据，false=走真实接口
    mockDelay: 100
}
```

- 接口没通时保持 `useMock: true`，图表用 `src/mock/index.js` 里的假数据渲染，页面不会白屏。
- 接口调通后改成 `useMock: false`，组件代码一行都不用动；请求失败或 8 秒超时会自动回退假数据，方便演示。

## 4. 本地启动

```bash
npm run dev
```

端口 8083，浏览器打开 <http://localhost:8083>（hash 路由，可直接访问 `/#/home`、`/#/disease`、`/#/drug`）。

## 5. 打包

```bash
npm run build
```

产物在 `dist/`，`index.html` 里资源用相对路径（`publicPath: './'`），整体丢到 Tomcat `webapps/dist` 即可访问。

内存不足时：

```bash
# Windows PowerShell
$env:NODE_OPTIONS="--max-old-space-size=4096"
# Linux / macOS
export NODE_OPTIONS=--max-old-space-size=4096
```

## 6. 目录说明

```
src/
├── config.js                 接口地址与真假数据开关（部署只改这里）
├── main.js                   入口：注册路由、请求库、假数据适配层
├── api/index.js              请求适配层（useMock 开关在这里生效）
├── mock/index.js             12 个接口的假数据 + 首页概览指标
├── router/index.js           路由表
├── components/
│   ├── home/                 首页概览、城市等级竞争、年龄患病比例、Top10 销额、各省份销量
│   ├── disease/              联合用药、药品组合、疾病年龄分布、科室分布
│   └── drug/                 覆盖城市、覆盖医院、对应适应症、科室分布
├── extends/                  Vue / Array 扩展方法
└── assets/                   样式与图片
build/                        webpack 配置
config/                       dev / prod 环境变量与端口
static/                       模板遗留静态资源（打包时原样复制到 dist/static）
```

## 7. 常见报错

| 报错 | 原因 | 处理 |
| --- | --- | --- |
| `Unexpected token` / 编译直接失败 | Node 版本过高 | 降到 14.16.1 |
| `EPERM: operation not permitted, mkdir '...\AppData\Roaming\npm'` | 用户级 `~/.npmrc` 里的 `prefix` 指向一个建不出来的目录（安全软件或权限策略拦截） | 把 `prefix` 改成可写路径，如 `npm config set prefix D:\npm-global`；`cache` 同理 |
| `npm update check failed` 黄框 | npm 6 的更新检查写 `~/.config` 失败，不影响构建 | 在 `~/.npmrc` 加一行 `update-notifier=false` |
| `JavaScript heap out of memory` | 内存不够 | 见上面 `NODE_OPTIONS` |
| `Module not found` | 依赖没装全 | 删掉 `node_modules` 重新 `npm install` |
| 图表空着、只有 loading | 接口没通 | 确认 `src/config.js` 的 `useMock`/`baseUrl` |

## 8. 已知事项

- 药品覆盖城市原来是百度地图（依赖外网 bmap + ak），离线环境出不了图，已改成柱状图。
- 原工程里「联合用药」组件请求的是 `/disease/drug`、「药品组合」组件请求的是 `/disease/union`，与接口表的名称是交叉的，后端实现前需要和前端确认。
