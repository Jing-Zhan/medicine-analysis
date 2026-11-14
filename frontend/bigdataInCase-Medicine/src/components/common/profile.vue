<template>
    <div class="mod">
        <div class="mod-head">
            <span class="mod-title">{{ title }}</span>
            <span class="mod-tabs" v-if="mode === 'disease'">
                <a v-for="t in tabs"
                   :key="t.key"
                   href="javascript:;"
                   :class="['mod-tab', t.key === active ? 'on' : '']"
                   @click="switchTab(t.key)">{{ t.label }}</a>
            </span>
            <span class="mod-note">{{ note }}</span>
        </div>

        <div v-if="loading" class="mod-empty">数据加载中</div>
        <div v-else-if="error" class="mod-empty">{{ error }}</div>
        <div v-else-if="mode === 'drug'" class="mod-drug">
            <div class="kpis">
                <div class="kpi" v-for="k in indicators" :key="k.Label">
                    <div class="kpi-val">{{ k.Value }}<em>%</em></div>
                    <div class="kpi-lab">{{ k.Label }}</div>
                </div>
            </div>

            <div class="market-head">
                <span class="market-title">厂商销售份额前十</span>
                <span class="market-meta">
                    厂商总数 {{ fmt(vendorCount) }}　
                    CR10 {{ cr10 }}%　
                    HHI {{ fmt(hhi) }}
                </span>
            </div>
            <div class="vendors">
                <div class="vendor-row" v-for="(v, i) in vendors" :key="v.Name">
                    <span class="vendor-rank">{{ i + 1 }}</span>
                    <span class="vendor-name" :title="v.Name">{{ v.Name }}</span>
                    <span class="vendor-track">
                        <span class="vendor-fill" :style="{ width: barWidth(v.Share, 8) }"></span>
                    </span>
                    <span class="vendor-amount">{{ fmt(v.Amount) }}</span>
                    <span class="vendor-share">{{ v.Share }}%</span>
                </div>
                <div class="mod-empty" v-if="!vendors.length">暂无厂商数据</div>
            </div>
        </div>

        <div v-else class="mod-disease">
            <table class="tbl">
                <thead>
                <tr>
                    <th class="c">#</th>
                    <th>疾病分类</th>
                    <th class="r">处方数</th>
                    <th class="r">总金额 元</th>
                    <th class="r">均次费用 元</th>
                    <th class="r">占比</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(it, i) in burden" :key="it.Name">
                    <td class="c">{{ i + 1 }}</td>
                    <td class="name" :title="it.Name">{{ it.Name }}</td>
                    <td class="r">{{ fmt(it.Records) }}</td>
                    <td class="r">{{ fmt(it.Amount) }}</td>
                    <td class="r strong">{{ fmt(it.AvgAmount) }}</td>
                    <td class="r">{{ it.Share }}%</td>
                </tr>
                <tr v-if="!burden.length">
                    <td colspan="6" class="c mod-empty">暂无数据</td>
                </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
    import Vue from 'vue'

    export default {
        name: 'profile',
        props: {
            mode: {
                type: String,
                default: 'disease'
            }
        },
        data() {
            const tabs = [
                {key: 'cat', label: '大类', param: 11},
                {key: 'sub', label: '中类', param: 12},
                {key: 'item', label: '细目', param: 13}
            ]
            return {
                tabs: tabs,
                active: 'cat',
                loading: false,
                error: '',
                burden: [],
                indicators: [],
                vendors: [],
                vendorCount: 0,
                cr10: 0,
                hhi: 0
            }
        },
        computed: {
            title() {
                return this.mode === 'drug' ? '用药结构与厂商份额' : '疾病费用负担'
            },
            note() {
                return this.mode === 'drug'
                    ? '占比按处方数加权，CR10 为前十厂商金额占比，HHI 越小越分散'
                    : '均次费用为该类的总金额除以处方数，用于区分「人多」与「花钱多」'
            }
        },
        mounted() {
            this.load()
        },
        methods: {
            switchTab(key) {
                if (key === this.active) return
                this.active = key
                this.load()
            },
            load() {
                var self = this
                self.loading = true
                self.error = ''
                if (self.mode === 'drug') {
                    Vue.ajax.send({
                        url: '/drug/overview',
                        data: {},
                        success: function (res) {
                            self.loading = false
                            if (!!res && res.code == '200' && res.data) {
                                var d = res.data
                                self.indicators = d.Indicators || []
                                self.vendors = d.Vendors || []
                                self.vendorCount = d.VendorCount || 0
                                self.cr10 = d.Cr10 || 0
                                self.hhi = d.Hhi || 0
                            } else {
                                self.error = (res && res.msg) ? res.msg : '查询失败'
                            }
                        },
                        error: function () {
                            self.loading = false
                            self.error = '接口请求失败'
                        }
                    })
                    return
                }
                var level = 11
                for (var i = 0; i < self.tabs.length; i++) {
                    if (self.tabs[i].key === self.active) level = self.tabs[i].param
                }
                Vue.ajax.send({
                    url: '/disease/burden',
                    data: {level: level},
                    success: function (res) {
                        self.loading = false
                        if (!!res && res.code == '200' && res.data) {
                            self.burden = res.data || []
                        } else {
                            self.error = (res && res.msg) ? res.msg : '查询失败'
                        }
                    },
                    error: function () {
                        self.loading = false
                        self.error = '接口请求失败'
                    }
                })
            },
            fmt(v) {
                if (v === null || v === undefined || v === '') return '0'
                var n = Number(v)
                if (isNaN(n)) return String(v)
                return n.toLocaleString('zh-CN')
            },
            barWidth(share, full) {
                var n = Number(share)
                if (isNaN(n) || n <= 0) return '0%'
                var w = n / full * 100
                if (w > 100) w = 100
                return (w < 2 ? 2 : w) + '%'
            }
        }
    }
</script>

<style scoped>
    .mod {
        clear: both;
        width: 100%;
        margin-top: 20px;
        background: #fff;
        border: 1px solid #e2e8f0;
        padding: 16px 18px 16px;
        box-sizing: border-box;
    }

    .mod-head {
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }

    .mod-title {
        font-size: 16px;
        color: #1f5fa8;
        font-weight: 600;
        margin-right: 16px;
        white-space: nowrap;
    }

    .mod-tabs {
        flex: 1;
    }

    .mod-tab {
        display: inline-block;
        padding: 3px 12px;
        margin-right: 6px;
        font-size: 13px;
        color: #4a5b6d;
        border: 1px solid #d7e0ea;
        background: #f7fafc;
        text-decoration: none;
    }

    .mod-tab.on {
        color: #fff;
        background: #1f5fa8;
        border-color: #1f5fa8;
    }

    .mod-note {
        font-size: 12px;
        color: #8496a8;
    }

    .mod-empty {
        padding: 28px 0;
        text-align: center;
        color: #8496a8;
        font-size: 13px;
    }

    /* ---------- 指标卡 ---------- */
    .kpis {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
    }

    .kpi {
        flex: 1 1 0;
        border: 1px solid #e8eef5;
        border-top: 3px solid #1f5fa8;
        background: #f6fafd;
        padding: 12px 14px;
    }

    .kpi-val {
        font-size: 22px;
        font-weight: 600;
        color: #1f5fa8;
        line-height: 1.2;
        font-variant-numeric: tabular-nums;
    }

    .kpi-val em {
        font-style: normal;
        font-size: 13px;
        margin-left: 2px;
    }

    .kpi-lab {
        font-size: 12.5px;
        color: #6b7c8f;
        margin-top: 4px;
    }

    /* ---------- 厂商 ---------- */
    .market-head {
        display: flex;
        align-items: baseline;
        margin-bottom: 8px;
    }

    .market-title {
        font-size: 13px;
        color: #1f5fa8;
        margin-right: 14px;
    }

    .market-meta {
        font-size: 12.5px;
        color: #6b7c8f;
    }

    .vendor-row {
        display: flex;
        align-items: center;
        font-size: 13px;
        padding: 4px 0;
    }

    .vendor-rank {
        flex: 0 0 24px;
        color: #8496a8;
        text-align: center;
    }

    .vendor-name {
        flex: 0 0 260px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #33414f;
        padding-right: 12px;
    }

    .vendor-track {
        flex: 1 1 auto;
        height: 10px;
        background: #eef2f7;
        margin-right: 12px;
    }

    .vendor-fill {
        display: block;
        height: 10px;
        background: #5b9bd5;
    }

    .vendor-amount {
        flex: 0 0 110px;
        text-align: right;
        color: #33414f;
        font-variant-numeric: tabular-nums;
        padding-right: 14px;
    }

    .vendor-share {
        flex: 0 0 64px;
        text-align: right;
        color: #6b7c8f;
        font-variant-numeric: tabular-nums;
    }

    /* ---------- 费用表 ---------- */
    .tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .tbl th {
        text-align: left;
        font-weight: 600;
        color: #6b7c8f;
        border-bottom: 1px solid #e2e8f0;
        padding: 7px 8px;
        white-space: nowrap;
    }

    .tbl td {
        padding: 7px 8px;
        border-bottom: 1px solid #f1f5f9;
        color: #33414f;
    }

    .tbl tbody tr:hover {
        background: #f7fafd;
    }

    .tbl .r {
        text-align: right;
        font-variant-numeric: tabular-nums;
    }

    .tbl .c {
        text-align: center;
    }

    .tbl .name {
        max-width: 420px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .tbl .strong {
        color: #1f5fa8;
        font-weight: 600;
    }

    @media (max-width: 1200px) {
        .mod-note {
            display: none;
        }

        .vendor-name {
            flex: 0 0 180px;
        }

        .kpis {
            flex-wrap: wrap;
        }

        .kpi {
            flex: 1 1 30%;
        }
    }
</style>
