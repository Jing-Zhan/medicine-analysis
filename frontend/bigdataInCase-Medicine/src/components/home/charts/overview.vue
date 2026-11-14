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
    margin-top: 14px;
    background: #fbfcfc;
    border: 1px solid #eef2f4;
    border-radius: 12px;
    padding: 6px 4px;
}
.overview-item{
    flex: 1;
    min-width: 170px;
    padding: 12px 18px;
    text-align: left;
    position: relative;
}
.overview-item + .overview-item:before{
    content: "";
    position: absolute;
    left: 0;
    top: 14px;
    bottom: 14px;
    width: 1px;
    background: #e6ecef;
}
.overview-value{
    font-size: 30px;
    line-height: 40px;
    color: #1f6f5c;
    font-weight: 700;
    letter-spacing: .5px;
    font-variant-numeric: tabular-nums;
}
.overview-unit{
    font-size: 13px;
    font-weight: 500;
    color: #74838e;
    margin-left: 4px;
}
.overview-label{
    font-size: 13px;
    color: #74838e;
    letter-spacing: .2px;
}
@media (max-width: 1400px) {
    .overview-value{
        font-size: 24px;
        line-height: 32px;
    }
    .overview-label{
        font-size: 12px;
    }
    .overview-item{
        padding: 8px 14px;
    }
}
</style>
