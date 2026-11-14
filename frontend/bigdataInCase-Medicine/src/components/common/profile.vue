<template>
    <div class="comp">
        <div class="comp-head">
            <span class="comp-title">{{ title }}</span>
            <span class="comp-tabs">
                <a v-for="t in tabs"
                   :key="t.key"
                   href="javascript:;"
                   :class="['comp-tab', t.key === active ? 'on' : '']"
                   @click="switchTab(t.key)">{{ t.label }}</a>
            </span>
            <span class="comp-note">{{ note }}</span>
        </div>

        <div v-if="loading" class="comp-empty">数据加载中</div>
        <div v-else-if="error" class="comp-empty">{{ error }}</div>
        <div v-else-if="!items.length" class="comp-empty">暂无数据</div>

        <div v-else class="comp-list">
            <div class="comp-row" v-for="(it, i) in items" :key="it.Name">
                <span class="comp-name" :title="it.Name">{{ it.Name }}</span>
                <span class="comp-track">
                    <span class="comp-fill" :style="{ width: barWidth(it.Ratio) }"></span>
                </span>
                <span class="comp-count">{{ fmt(it.Counter) }}</span>
                <span class="comp-ratio">{{ it.Ratio }}%</span>
            </div>
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
            const diseaseTabs = [
                {key: 'cat', label: '大类', param: 11},
                {key: 'sub', label: '中类', param: 12},
                {key: 'item', label: '细目', param: 13}
            ]
            const drugTabs = [
                {key: 'form_name1', label: '剂型', param: 'form_name1'},
                {key: 'is_essential_drug', label: '基本药物', param: 'is_essential_drug'},
                {key: 'is_otc', label: '非处方药', param: 'is_otc'},
                {key: 'is_special_drug', label: '特殊管理', param: 'is_special_drug'},
                {key: 'risk_pregnancy_grade', label: '妊娠风险', param: 'risk_pregnancy_grade'}
            ]
            const tabs = this.mode === 'drug' ? drugTabs : diseaseTabs
            return {
                tabs: tabs,
                active: tabs[0].key,
                loading: false,
                error: '',
                items: []
            }
        },
        computed: {
            title() {
                return this.mode === 'drug' ? '药品属性构成' : '疾病分层构成'
            },
            note() {
                return '占比为该类处方数占全库的比例'
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
            currentTab() {
                for (var i = 0; i < this.tabs.length; i++) {
                    if (this.tabs[i].key === this.active) return this.tabs[i]
                }
                return this.tabs[0]
            },
            load() {
                var self = this
                var tab = self.currentTab()
                var url = self.mode === 'drug' ? '/drug/attribute' : '/disease/category'
                var data = self.mode === 'drug' ? {type: tab.param} : {level: tab.param}
                self.loading = true
                self.error = ''
                Vue.ajax.send({
                    url: url,
                    data: data,
                    success: function (res) {
                        self.loading = false
                        if (!!res && res.code == '200' && res.data) {
                            self.items = res.data || []
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
            barWidth(ratio) {
                var n = Number(ratio)
                if (isNaN(n) || n <= 0) return '0%'
                // 以 40% 为满格，超过则截断，使头部差异可见
                var w = n / 40 * 100
                if (w > 100) w = 100
                return (w < 2 ? 2 : w) + '%'
            }
        }
    }
</script>

<style scoped>
    .comp {
        clear: both;
        width: 100%;
        margin-top: 20px;
        background: #fff;
        border: 1px solid #e2e8f0;
        padding: 16px 18px 14px;
        box-sizing: border-box;
    }

    .comp-head {
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }

    .comp-title {
        font-size: 16px;
        color: #1f5fa8;
        font-weight: 600;
        margin-right: 16px;
        white-space: nowrap;
    }

    .comp-tabs {
        flex: 1;
    }

    .comp-tab {
        display: inline-block;
        padding: 3px 12px;
        margin-right: 6px;
        font-size: 13px;
        color: #4a5b6d;
        border: 1px solid #d7e0ea;
        background: #f7fafc;
        text-decoration: none;
    }

    .comp-tab.on {
        color: #fff;
        background: #1f5fa8;
        border-color: #1f5fa8;
    }

    .comp-note {
        font-size: 12px;
        color: #8496a8;
        white-space: nowrap;
    }

    .comp-empty {
        padding: 32px 0;
        text-align: center;
        color: #8496a8;
        font-size: 13px;
    }

    .comp-list {
        padding: 2px 0;
    }

    .comp-row {
        display: flex;
        align-items: center;
        padding: 5px 0;
        font-size: 13px;
    }

    .comp-name {
        flex: 0 0 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #33414f;
        padding-right: 12px;
    }

    .comp-track {
        flex: 1 1 auto;
        height: 10px;
        background: #eef2f7;
        margin-right: 12px;
    }

    .comp-fill {
        display: block;
        height: 10px;
        background: #5b9bd5;
    }

    .comp-count {
        flex: 0 0 92px;
        text-align: right;
        color: #33414f;
        font-variant-numeric: tabular-nums;
        padding-right: 14px;
    }

    .comp-ratio {
        flex: 0 0 62px;
        text-align: right;
        color: #6b7c8f;
        font-variant-numeric: tabular-nums;
    }

    @media (max-width: 1200px) {
        .comp-name {
            flex: 0 0 200px;
        }

        .comp-note {
            display: none;
        }
    }
</style>
