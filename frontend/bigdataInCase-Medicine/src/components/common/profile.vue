<template>
    <div class="profile">
        <div class="profile-head">
            <span class="profile-title">{{ title }}</span>
            <span class="profile-note">按提升度排序，大于 1 表示对该对象有额外倾向</span>
            <span class="profile-search">
                <input type="text" v-model="q" :placeholder="searchHint" @keyup.enter="getProfile()">
                <a href="javascript:;" @click="getProfile()">检索</a>
            </span>
        </div>

        <div v-if="loading" class="profile-empty">数据加载中</div>
        <div v-else-if="error" class="profile-empty">{{ error }}</div>
        <div v-else-if="!target" class="profile-empty">暂无数据</div>

        <div v-else>
            <!-- 目标对象 -->
            <div class="profile-target">
                <div class="t-name">{{ target.Name }}</div>
                <div class="t-meta">
                    <span v-if="target.Category">{{ target.Category }}　›　{{ target.SubCategory }}　›</span>
                    <span>处方 {{ fmt(target.Records) }} 条</span>
                    <span>金额 {{ fmt(target.Amount) }} 元</span>
                    <span>占全库 {{ target.Share }}%</span>
                </div>
            </div>

            <div class="profile-body">
                <!-- 关联强度榜 -->
                <div class="profile-block wide">
                    <div class="block-title">{{ itemLabel }}　关联强度</div>
                    <table class="tbl">
                        <thead>
                        <tr>
                            <th class="c">#</th>
                            <th>名称</th>
                            <th class="r">次数</th>
                            <th class="r">置信度</th>
                            <th class="r">提升度</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr v-for="(it, i) in items" :key="it.Code">
                            <td class="c">{{ i + 1 }}</td>
                            <td class="name" :title="it.Name">{{ it.Name }}</td>
                            <td class="r">{{ fmt(it.Count) }}</td>
                            <td class="r">{{ pct(it.Conf) }}</td>
                            <td class="r"><span :class="['lift', it.Lift >= 1 ? 'up' : 'flat']">{{ it.Lift }}</span></td>
                        </tr>
                        <tr v-if="!items.length">
                            <td colspan="5" class="c empty-cell">样本不足，未形成关联</td>
                        </tr>
                        </tbody>
                    </table>
                </div>

                <div class="profile-side">
                    <!-- 年龄段 -->
                    <div class="profile-block">
                        <div class="block-title">年龄段占比</div>
                        <div class="bars">
                            <div class="bar-row" v-for="(label, i) in structure.AgeRange" :key="label">
                                <span class="bar-label">{{ label }}</span>
                                <span class="bar-track">
                                    <span class="bar-fill" :style="{ width: barWidth(structure.AgeShare[i]) }"></span>
                                </span>
                                <span class="bar-value">{{ structure.AgeShare[i] }}%</span>
                            </div>
                        </div>
                    </div>

                    <!-- 科室 -->
                    <div class="profile-block">
                        <div class="block-title">科室前五</div>
                        <ul class="rank">
                            <li v-for="g in structure.Sections" :key="g.Name">
                                <span class="rank-name">{{ g.Name }}</span>
                                <em>{{ fmt(g.Count) }}</em>
                            </li>
                            <li v-if="!structure.Sections.length" class="rank-empty">暂无数据</li>
                        </ul>
                    </div>

                    <!-- 地区与标签 -->
                    <div class="profile-block">
                        <div class="block-title">{{ structure.AreaLabel }}前五</div>
                        <ul class="rank">
                            <li v-for="g in structure.Areas" :key="g.Name">
                                <span class="rank-name">{{ g.Name }}</span>
                                <em>{{ fmt(g.Count) }}</em>
                            </li>
                            <li v-if="!structure.Areas.length" class="rank-empty">暂无数据</li>
                        </ul>
                        <div class="tags">
                            <span class="tag" v-for="t in tags" :key="t.Label">{{ t.Label }}　{{ t.Value }}</span>
                        </div>
                    </div>
                </div>
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
                q: '',
                loading: false,
                error: '',
                target: null,
                items: [],
                itemLabel: '',
                structure: {AgeRange: [], AgeShare: [], Sections: [], Areas: [], AreaLabel: ''},
                tags: []
            }
        },
        computed: {
            title() {
                return this.mode === 'drug' ? '药品画像' : '适应症画像'
            },
            searchHint() {
                return this.mode === 'drug' ? '输入药品名称' : '输入适应症名称'
            },
            api() {
                return this.mode === 'drug' ? '/drug/profile' : '/disease/profile'
            }
        },
        mounted() {
            this.getProfile()
        },
        methods: {
            /**
             * 拉取画像。不传参数时后端返回处方量最大的对象，
             * 保证页面初次打开就有内容。
             */
            getProfile(keyword) {
                var self = this
                if (keyword !== undefined && keyword !== null && String(keyword).trim() !== '') {
                    self.q = String(keyword).trim()
                }
                self.loading = true
                self.error = ''
                Vue.ajax.send({
                    url: self.api,
                    data: {keyword: self.q || ''},
                    success: function (res) {
                        self.loading = false
                        if (!!res && res.code == '200' && res.data) {
                            self.apply(res.data)
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
            apply(d) {
                this.target = d.Target || null
                this.items = d.Items || []
                this.itemLabel = d.ItemLabel || ''
                var st = d.Structure || {}
                this.structure = {
                    AgeRange: st.AgeRange || [],
                    AgeShare: st.AgeShare || [],
                    Sections: st.Sections || [],
                    Areas: st.Areas || [],
                    AreaLabel: st.AreaLabel || '地区'
                }
                this.tags = d.Tags || []
            },
            fmt(v) {
                if (v === null || v === undefined || v === '') return '0'
                var n = Number(v)
                if (isNaN(n)) return String(v)
                return n.toLocaleString('zh-CN')
            },
            pct(v) {
                var n = Number(v)
                if (isNaN(n)) return '0%'
                return (n * 100).toFixed(1) + '%'
            },
            barWidth(share) {
                var n = Number(share)
                if (isNaN(n) || n <= 0) return '0%'
                var w = Math.min(100, n / 25 * 100)
                return (w < 2 ? 2 : w) + '%'
            }
        }
    }
</script>

<style scoped>
    .profile {
        clear: both;
        width: 100%;
        margin-top: 20px;
        background: #fff;
        border: 1px solid #e2e8f0;
        padding: 16px 18px 18px;
        box-sizing: border-box;
    }

    .profile-head {
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 12px;
        margin-bottom: 14px;
    }

    .profile-title {
        font-size: 16px;
        color: #1f5fa8;
        font-weight: 600;
        margin-right: 12px;
    }

    .profile-note {
        font-size: 12px;
        color: #8496a8;
        flex: 1;
    }

    .profile-search input {
        width: 180px;
        height: 28px;
        padding: 0 10px;
        border: 1px solid #cfd9e4;
        font-size: 13px;
        outline: none;
    }

    .profile-search a {
        display: inline-block;
        height: 28px;
        line-height: 28px;
        padding: 0 14px;
        margin-left: 8px;
        background: #1f5fa8;
        color: #fff;
        font-size: 13px;
        text-decoration: none;
        vertical-align: top;
    }

    .profile-empty {
        padding: 40px 0;
        text-align: center;
        color: #8496a8;
        font-size: 13px;
    }

    .profile-target {
        margin-bottom: 14px;
    }

    .t-name {
        font-size: 18px;
        color: #15202b;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .t-meta span {
        font-size: 12.5px;
        color: #6b7c8f;
        margin-right: 18px;
    }

    .profile-body {
        display: flex;
        gap: 16px;
        align-items: flex-start;
    }

    .profile-block {
        border: 1px solid #e8eef5;
        padding: 12px 14px;
        margin-bottom: 12px;
    }

    .profile-block.wide {
        flex: 1 1 auto;
        min-width: 0;
        margin-bottom: 0;
    }

    .profile-side {
        flex: 0 0 360px;
        width: 360px;
    }

    .profile-side .profile-block:last-child {
        margin-bottom: 0;
    }

    .block-title {
        font-size: 13px;
        color: #1f5fa8;
        margin-bottom: 10px;
    }

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
        padding: 6px 8px;
        white-space: nowrap;
    }

    .tbl td {
        padding: 6px 8px;
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
        max-width: 320px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .tbl .empty-cell {
        color: #8496a8;
        padding: 24px 0;
    }

    .lift {
        display: inline-block;
        min-width: 44px;
        padding: 0 6px;
        line-height: 20px;
        border-radius: 2px;
        font-size: 12px;
    }

    .lift.up {
        background: #eaf5ee;
        color: #2f7d5d;
    }

    .lift.flat {
        background: #f2f4f7;
        color: #8496a8;
    }

    .bars {
        font-size: 12.5px;
    }

    .bar-row {
        display: flex;
        align-items: center;
        margin-bottom: 7px;
    }

    .bar-label {
        flex: 0 0 78px;
        color: #6b7c8f;
    }

    .bar-track {
        flex: 1 1 auto;
        height: 9px;
        background: #eef2f7;
        margin: 0 8px;
    }

    .bar-fill {
        display: block;
        height: 9px;
        background: #5b9bd5;
    }

    .bar-value {
        flex: 0 0 46px;
        text-align: right;
        color: #33414f;
        font-variant-numeric: tabular-nums;
    }

    .rank {
        list-style: none;
        margin: 0;
        padding: 0;
        font-size: 12.5px;
    }

    .rank li {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        border-bottom: 1px dashed #eef2f7;
    }

    .rank li:last-child {
        border-bottom: none;
    }

    .rank-name {
        color: #33414f;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: 10px;
    }

    .rank em {
        font-style: normal;
        color: #6b7c8f;
        font-variant-numeric: tabular-nums;
    }

    .rank-empty {
        color: #8496a8;
    }

    .tags {
        margin-top: 10px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }

    .tag {
        font-size: 12px;
        color: #33414f;
        background: #f4f7fb;
        border: 1px solid #e2e8f0;
        padding: 2px 8px;
    }

    @media (max-width: 1440px) {
        .profile-side {
            flex: 0 0 300px;
            width: 300px;
        }
    }

    @media (max-width: 1100px) {
        .profile-body {
            display: block;
        }

        .profile-side {
            width: auto;
            margin-top: 12px;
        }
    }
</style>
