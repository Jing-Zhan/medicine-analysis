<template>
    <div class="main-left chart">
        <div class="case-title">城市等级竞争图表</div>
        <echart class="case-chart" :options="option"/>
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
            color:['#b5a2de','#b5a2de','#5ab2ef','#5ab2ef','#de7984','#de7984','#5fccc3','#5fccc3','#f7a25a','#f7a25a'],
            grid:{
                top:20,
                bottom:20,
                left: 60,
                right: 40
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    label: {
                        backgroundColor: '#283b56'
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
                            color : '#b8cde3'
                        } 
                    },
                    axisLabel:{
                        show : true,
                        color:'#b8cde3'
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
                    color:'#b8cde3'
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
                        color:'#bac8d5',
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
                        self.option.xAxis[0].data=data.data.YearData;
                        var newArr=[];
                        data.data.CityData.forEach(item => {
                            newArr.push({
                                name: item.Level+'销额',
                                type: 'bar',
                                stack: '总量',
                                itemStyle:{
                                    barBorderRadius:4,
                                    borderColor:'#fff'
                                },
                                data: item.BarData
                            },{
                                name: item.Level+'增长率',
                                type: 'line',
                                symbol: 'diamond',
                                yAxisIndex: 1,
                                symbolSize: 5,
                                data: item.LineData
                            })
                        });
                        self.option.series=newArr;
                    }
                }
            }); 
        }
    }
};
</script>
<style scoped>
</style>