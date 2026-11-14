<template>
    <div class="age chart">
                    <div class="case-title">不同年龄患病比例分析</div>
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
            color:['#3E8EDC','#CF8A2C'],
            grid:{
                top:20,
                bottom:20,
                left: 0,
                right: 0
            },
            tooltip: {},
            xAxis : [
                {
                    type : 'category',
                    data : ['0-3岁','3-6岁','6-12岁','12-20岁','20-30岁','30-40岁','40-50岁','50-60岁','60-70岁','70岁+'],
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
                }
            ],
            yAxis : [
                {
                    type : 'value',
                    axisTick: {
                        show: false
                    },
                    axisLine: {
                        show: false 
                    },
                    axisLabel:{
                        show: false
                    },
                    splitLine:{
                        show: false
                    }
                }
            ],
            series : [
                {
                    name:'男',
                    type:'bar',
                    barWidth:14,
                    itemStyle:{
                        barBorderRadius:2
                    },
                    data:[],

                },
                {
                    name:'女',
                    type:'bar',
                    barWidth:14,
                    itemStyle:{
                        barBorderRadius:2
                    },
                    data:[]
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
                url: "/home/age",
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {      
                        self.option.xAxis[0].data=data.data.AgeRange;
                        self.option.series[0].data=data.data.AgeData[0];
                        self.option.series[1].data=data.data.AgeData[1];
                    }
                }
            }); 
        }
    }
};
</script>
<style scoped>
</style>