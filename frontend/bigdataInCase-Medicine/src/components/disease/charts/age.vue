<template>
    <div class="main-right chart">
        <div class="case-title">目标适应症不同年龄人群分布</div>
        <echart ref="case" class="case-chart" :options="option"/>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/scatter'
import 'echarts/lib/chart/bar'
var mean=0;
export default {
  components: {
        echart:ECharts
  },
  props: {
        keyword: {
            type: String,
            default: '甲状腺'
        },
    },
  data() {
    return {
        nodata:false,
        option:{
            xAxis: {
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: true,
                    lineStyle : {
                        color : '#c4d6e7'
                    } 
                },
                axisLabel:{
                    show : false,
                },
                splitLine:{ show : false}
            },
            tooltip: {
                formatter: function (obj) {
                    return obj.seriesName+'<br>'+obj.data[1]+'岁：'+obj.data[0]
                }
            },
            yAxis: {
                axisTick: {
                        show: false
                },
                axisLine: {
                    show: true,
                    lineStyle : {
                        color : '#c4d6e7'
                    } 
                },
                axisLabel:{
                    show : true,
                    lineStyle : {
                        color : '#c4d6e7'
                    } 
                },
                splitLine:{ show : false}
            },
            series: [{
                symbolSize: function (data) {
                   return data[1]*data[0] / mean /2;
                },
                itemStyle:{
                    color:'#92c9ef'
                },
                name:'男',
                data: [],
                type: 'scatter'
            },{
                symbolSize: function (data) {
                   return data[1]*data[0] / mean /2;
                },
                itemStyle:{
                    color:'#ffadad'
                },
                data: [],
                name:'女',
                type: 'scatter'
            }]
      }
    };
  },
  mounted: function() {
      this.getSeries();
    },
    methods: {
        getSeries: function(){
            var self = this;
            self.nodata=false;
            self.$refs.case.showLoading({
                text: '',
                color: '#1988f9',
                maskColor: 'rgba(255, 255, 255, 1)'
            })
            Vue.ajax.send({
                url: "/disease/age?keyword="+this.keyword,
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {   
                         if(data.data.length>0){
                             var data1=data.data.filterProperty("Sex",'10'),
                                data2=data.data.filterProperty("Sex",'20'),
                                series1=[],series2=[],total=0;                        
                            data1.forEach(element => {
                                total=total+element.Counter;
                                series1.push([element.Counter,element.Age])
                            });
                            data2.forEach(element => {
                                total=total+element.Counter;
                                series2.push([element.Counter,element.Age])
                            });
                            mean=total/data.data.length;
                            self.option.series[0].data=series1;
                            self.option.series[1].data=series2;
                            self.$refs.case.hideLoading();
                         }else{
                            self.$refs.case.hideLoading();
                            self.nodata=true;
                        }   
                        
                    }
                }
            }); 
        }
    }
};
</script>