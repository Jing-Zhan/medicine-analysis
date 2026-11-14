<template>
    <div class="city chart">
        <div class="case-title">药品品牌覆盖城市图</div>
        <echart theme="med" ref="case" class="case-chart" :options="option" autoresize/>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/bar'
export default {
  components: {
        echart:ECharts
  },
  props: {
        keyword: {
            type: String,
            default: '人参'
        },
    },
  data() {
    return {
        nodata:false,
        option:{
            color:['#2E7DD1'],
            grid:{
                top:20,
                bottom:70,
                left:60,
                right:30
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: [],
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: true,
                    lineStyle : {
                        color : '#DFE6EB'
                    }
                },
                axisLabel:{
                    show: true,
                    color:'#16232E',
                    interval:0,
                    rotate:30,
                    formatter:function(value){
                        if(value.length>4){
                            return value.slice(0,4)+'...'
                        }  else {
                            return value;
                        }
                    }
                }
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
                    show: true,
                    color:'#16232E'
                },
                splitLine:{
                    lineStyle:{
                        color:'#E5EBEF'
                    }
                }
            },
            series: [{
                name: '覆盖医院数',
                type: 'bar',
                barMaxWidth: 26,
                itemStyle:{
                    barBorderRadius:4
                },
                data: []
            }]
        }
    }
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
                url: "/drug/cities?keyword="+self.keyword,
                data: {},
                success: function(data) {
                     if (!!data && data.code=='200') {
                        if(data.data.length>0){
                            var names=[],counters=[];
                            data.data.forEach(function(item){
                                names.push(item.Name);
                                counters.push(item.Counter);
                            })
                            self.option.xAxis.data=names;
                            self.option.series[0].data=counters;
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
