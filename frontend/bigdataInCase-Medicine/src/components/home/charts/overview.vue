<template>
    <div class="overview chart">
        <div class="case-title">首页概览</div>
        <div class="overview-list">
            <div class="overview-item" v-for="item in list" :key="item.label">
                <div class="overview-value">
                    {{ format(item.value) }}<span class="overview-unit">{{ item.unit }}</span>
                </div>
                <div class="overview-label">{{ item.label }}</div>
            </div>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
export default {
    data() {
        return {
            list: []
        }
    },
    mounted: function() {
        this.getList();
    },
    methods: {
        getList: function() {
            var self = this;
            Vue.ajax.send({
                url: "/home/overview",
                data: {},
                success: function(data) {
                    if (!!data && data.code == '200') {
                        self.list = data.data || [];
                    }
                }
            });
        },
        format: function(value) {
            if (value === null || value === undefined) {
                return '0';
            }
            return String(value).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        }
    }
}
</script>
<style scoped>
.overview-list{
    display: flex;
    flex-wrap: wrap;
    margin-top: 20px;
}
.overview-item{
    flex: 1;
    min-width: 160px;
    padding: 8px 12px;
    border-right: #ebedf6 1px solid;
    text-align: center;
}
.overview-item:last-child{
    border-right: none;
}
.overview-value{
    font-size: 30px;
    line-height: 42px;
    color: #1988f9;
    font-weight: bold;
}
.overview-unit{
    font-size: 14px;
    font-weight: normal;
    color: #697f94;
    margin-left: 2px;
}
.overview-label{
    font-size: 14px;
    color: #697f94;
}
@media (max-width: 1400px) {
    .overview-value{
        font-size: 22px;
        line-height: 32px;
    }
    .overview-label{
        font-size: 12px;
    }
}
</style>
