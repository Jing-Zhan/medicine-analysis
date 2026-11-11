<template>
    <div class="main-foot chart">
            <div class="case-title">各省份增长格局图表</div>
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
            grid:{
                top:10,
                bottom:40,
                left: 60,
                right: 60
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
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
                        color:'#b8cde3',
                        interval:0,
                        rotate:30,
                        formatter:function(value){
                            if(value.length>4){
                                return value.slice(0,4)+'...'
                            }  else {
                                return value;
                            } 
                        }
                    },
            }],
            yAxis: [{
                type:'value',
                min: 0,
                splitNumber:4,
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
                min:0,
                splitNumber:4,
                axisTick: {
                        show: false
                    },
                    axisLine: {
                        show: false
                    },
                    axisLabel:{
                        show : true,
                        color:'#bac8d5'
                        //formatter:'{value}%'
                    },
            }],
            series: [
                {
                    name: '销额',
                    type: 'bar',
                    stack: '总量',
                    itemStyle:{
                        barBorderRadius:4,
                        borderColor:'#fff',
                        color:'#5ab2ef'
                    },
                    data: [320, 302, 301, 334, 390]
                },
                {
                    name: '销量',
                    type: 'line',
                    itemStyle:{
                        color:'#ff7e00'
                    },
                    symbol: 'circle',
                    yAxisIndex: 1,
                    symbolSize: 5,
                    data: [20, 30, 50, 24, 34]
                }
            ]
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
                url: "/home/province",
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {      
                        //self.option.series[0].data=data.result;
                        var names=[],data1=[],data2=[];
                        for (let i = 0; i < data.data.length; i++) {
                            if(data.data[i].Name!=null){
                                names.push(data.data[i].Name);
                                data1.push(data.data[i].Amount)
                                data2.push(data.data[i].Counter)
                            }                            
                        }
                        self.option.xAxis[0].data=names;
                        self.option.series[0].data=data1;
                        self.option.series[1].data=data2;
                    }
                }
            }); 
        }
    }
};
</script>
<style scoped>
</style>