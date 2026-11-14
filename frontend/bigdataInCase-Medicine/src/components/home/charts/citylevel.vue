<template>
    <div class="main-left chart">
        <div class="case-title">城市等级竞争图表</div>
        <echart theme="med" class="case-chart" :options="option"/>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/line'
import 'echarts/lib/chart/bar'
export default {
  components: {
        echart:ECharts
  },
  data() {
    return {
        option:{
            color:['#6B7FD7','#6B7FD7','#2E7DD1','#2E7DD1','#D9695F','#D9695F','#2FA98C','#2FA98C','#CF8A2C','#CF8A2C'],
            grid:{
                top:30,
                bottom:20,
                // 金额是八位数（约 8,000,000），左侧留 80 否则刻度数字会被裁掉
                left: 80,
                right: 40
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#16232E'
                    }
                }
            },
            xAxis: [{
                type:'category',
                data: [],
                axisPointer:{
                    type:'shadow'
                },
                axisTick: {
                        show: false
                    },
                    axisLine: {
                        show: true,
                        lineStyle : {
                            color : '#6E7B87'
                        } 
                    },
                    axisLabel:{
                        show : true,
                        color:'#6E7B87'
                    },
            }],
            yAxis: [{
                type:'value',
                min: 0,
                axisTick: {
                        show: false
                    },
                axisLine: {
                    show: false
                },
                axisLabel:{
                    show : true,
                    color:'#6E7B87'
                }
            },{
                type:'value',
                axisTick: {
                        show: false
                    },
                    axisLine: {
                        show: false
                    },
                    axisLabel:{
                        show : true,
                        color:'#6E7B87',
                        formatter:'{value}%'
                    },
            }],
            series: []
        },
    };
  },
  mounted: function() {
      this.getSeries();
    },
    methods: {
        getSeries: function(){
            var self = this;
            Vue.ajax.send({
                url: "/home/citylevel",
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {
                        // 接口返回结构：{ YearData: ["200812"], CityData: [{Level, BarData:[金额], LineData:[]}] }
                        //
                        // 原实现把「年份」当横轴、把各等级堆叠到同一根柱子上。但数据集只覆盖
                        // 2008 年 12 月一个月，YearData 只有一个值，图上就只剩一根柱子，
                        // 5 个等级全挤在堆叠色块里，看不出"竞争"。
                        //
                        // 现在把横轴换成城市等级本身，柱高=该等级销售金额，按金额降序，
                        // 每个等级一根柱子，标题「城市等级竞争」才名副其实。
                        // LineData 是环比增长率，单期数据算不出来（接口返回空数组），故不再画折线。
                        var rows = (data.data.CityData || []).map(function (item) {
                            var v = (item.BarData && item.BarData.length) ? item.BarData[0] : 0;
                            return { level: item.Level, value: v };
                        });
                        rows.sort(function (a, b) { return b.value - a.value; });

                        self.option.xAxis[0].data = rows.map(function (r) { return r.level; });
                        self.option.series = [{
                            name: '销售金额',
                            type: 'bar',
                            barMaxWidth: 64,
                            itemStyle: {
                                barBorderRadius: 4,
                                borderColor: '#fff'
                            },
                            label: {
                                show: true,
                                position: 'top',
                                color: '#6E7B87',
                                fontSize: 11,
                                // 金额较大，统一折算成万元显示
                                formatter: function (p) { return (p.value / 10000).toFixed(1) + ' 万'; }
                            },
                            data: rows.map(function (r) { return r.value; })
                        }];
                    }
                }
            });
        }
    }
};
</script>
<style scoped>
</style>