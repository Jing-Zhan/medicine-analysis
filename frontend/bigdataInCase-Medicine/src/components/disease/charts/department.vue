<template>
    <div class="section chart">
        <div class="case-title">目标适应症对应科室分布</div>
        <echart ref="case" class="case-chart" :options="option"/>
        <div class="nodata" v-show="nodata">暂无数据</div>
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
            color:['#6ecbbc'],
            grid:{
                top:10,
                left: 10,
                right: 10
            },
            tooltip: {},
            xAxis: {
                type: 'category',
                data: [],
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
                    },
                    interval:0,
                    rotate:40,
                    formatter:function(value){
                        if(value.length>6){
                            return value.slice(0,6)+'...'
                        }  else {
                            return value;
                        } 
                    }
                },
                splitLine:{ show : false}
            },
            yAxis: {
                type: 'value',
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false
                },
                axisLabel:{
                    show : false
                },
                splitLine:{ show : false}
            },
            series: [{
                data: [],
                type: 'bar'
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
                url: "/disease/section?keyword="+this.keyword,
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {
                         if(data.data.length>0){
                             var data1=[],data2=[];    
                            data.data.forEach(element => {
                                data1.push(element.SectionName);
                                data2.push(element.Counter);
                            });
                            self.option.xAxis.data=data1;
                            self.option.series[0].data=data2;
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