<template>
    <div class="mod">
        <div class="mod-head">
            <span class="mod-title">{{ title }}</span>
            <span class="mod-note">{{ note }}</span>
        </div>

        <div v-if="loading" class="mod-empty">数据加载中</div>
        <div v-else-if="error" class="mod-empty">{{ error }}</div>
        <div v-else>
            <table class="tbl">
                <thead>
                <tr>
                    <th class="c">#</th>
                    <th>{{ nameLabel }}</th>
                    <th class="r">处方数</th>
                    <th class="r">注射剂占比</th>
                    <th class="r">基本药物占比</th>
                    <th class="r">抗菌药物占比</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(it, i) in rows" :key="it.Name">
                    <td class="c">{{ i + 1 }}</td>
                    <td class="name" :title="it.Name">{{ it.Name }}</td>
                    <td class="r">{{ fmt(it.Records) }}</td>
                    <td class="r">
                        <span class="rate">{{ fix(it.InjRate) }}%</span>
                        <span class="track"><span class="fill" :style="{ width: bar(it.InjRate) }"></span></span>
                    </td>
                    <td class="r">
                        <span class="rate">{{ fix(it.EssRate) }}%</span>
                        <span class="track"><span class="fill alt" :style="{ width: bar(it.EssRate) }"></span></span>
                    </td>
                    <td class="r">
                        <span class="rate">{{ fix(it.AntiRate) }}%</span>
                        <span class="track"><span class="fill warn" :style="{ width: bar(it.AntiRate) }"></span></span>
                    </td>
                </tr>
                <tr v-if="!rows.length">
                    <td colspan="6" class="mod-empty">暂无数据</td>
                </tr>
                </tbody>
            </table>

            <div class="mod-foot" v-if="rows.length">
                <span>注射剂占比 {{ fix(range.min) }}% 至 {{ fix(range.max) }}%，</span>
                <span>最高为 {{ range.maxName }}，最低为 {{ range.minName }}。</span>
                <span>{{ nameLabel }}按处方数取前 {{ rows.length }} 位。</span>
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
            return {
                loading: false,
                error: '',
                rows: []
            }
        },
        computed: {
            title() {
                return this.mode === 'drug' ? '各科室用药结构对比' : '各疾病大类用药结构对比'
            },
            nameLabel() {
                return this.mode === 'drug' ? '科室' : '疾病大类'
            },
            note() {
                return '占比按处方数加权，用于比较不同' + this.nameLabel + '的用药结构差异'
            },
            range() {
                var list = this.rows.slice()
                if (!list.length) return {min: 0, max: 0, minName: '', maxName: ''}
                list.sort(function (a, b) {
                    return Number(a.InjRate) - Number(b.InjRate)
                })
                return {
                    min: list[0].InjRate,
                    minName: list[0].Name,
                    max: list[list.length - 1].InjRate,
                    maxName: list[list.length - 1].Name
                }
            }
        },
        mounted() {
            this.load()
        },
        methods: {
            load() {
                var self = this
                self.loading = true
                self.error = ''
                Vue.ajax.send({
                    url: self.mode === 'drug' ? '/drug/structure' : '/disease/structure',
                    data: {limit: 10},
                    success: function (res) {
                        self.loading = false
                        if (!!res && res.code == '200' && res.data) {
                            self.rows = res.data || []
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
            fix(v) {
                var n = Number(v)
                if (isNaN(n)) return '0.00'
                return n.toFixed(2)
            },
            bar(v) {
                var n = Number(v)
                if (isNaN(n) || n <= 0) return '0%'
                if (n > 100) n = 100
                return (n < 2 ? 2 : n) + '%'
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

    .mod-foot {
        margin-top: 10px;
        font-size: 12px;
        color: #5a6b7d;
        line-height: 22px;
    }

    .tbl {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }

    .tbl th {
        background: #f4f7fb;
        color: #4a5b6d;
        font-weight: 600;
        text-align: left;
        padding: 8px 10px;
        border-bottom: 1px solid #e2e8f0;
        white-space: nowrap;
    }

    .tbl td {
        padding: 7px 10px;
        border-bottom: 1px solid #eef2f7;
        color: #33404d;
    }

    .tbl .c {
        text-align: center;
        width: 44px;
    }

    .tbl .r {
        text-align: right;
        white-space: nowrap;
    }

    .tbl .name {
        max-width: 260px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .tbl tbody tr:hover td {
        background: #f7fbff;
    }

    .rate {
        display: inline-block;
        min-width: 52px;
    }

    .track {
        display: inline-block;
        width: 70px;
        height: 6px;
        background: #edf1f6;
        vertical-align: middle;
        margin-left: 6px;
    }

    .fill {
        display: block;
        height: 6px;
        background: #2f7fd1;
    }

    .fill.alt {
        background: #35a97b;
    }

    .fill.warn {
        background: #e08c2f;
    }
</style>
