<template>
    <div class="hospital chart">
        <div class="case-title">药品品牌覆盖医院分析</div>
        <echart theme="med" ref="case" class="case-chart" :options="option"/>
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
            color:['#6B7FD7','#2E7DD1','#D9695F','#2FA98C'],
             tooltip : {
                trigger: 'axis',
                axisPointer : {            // 坐标轴指示器，坐标轴触发有效
                    type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            yAxis:  {
                type: 'value',
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: false,
                },
                axisLabel:{
                    show : false,
                },
                splitLine:{ show : false}
            },
            xAxis: {
                type: 'category',
                data:  [],
                axisTick: {
                    show: false
                },
                axisLine: {
                    show: true,
                    lineStyle : {
                        color : '#e8e8e8'
                    } 
                },
                axisLabel:{
                    show : true,
                    color:'#16232E',
                    interval:0,
                    rotate:20,
                    formatter:function(value){
                        if(value.length>6){
                            return value.slice(0,6)+'...'
                        }  else {
                            return value;
                        } 
                    }
                },
            },
            series: []
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
                url: "/drug/hospital?keyword="+self.keyword,
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {  
                        if(data.data.length>0){
                            var xData=[];
                            data.data.forEach((item,index)=>{
                                xData.push(item.Drug);
                            })
                            xData=xData.distinct();
                            var newArr=[{name:'一级',data:[]},{name:'二级',data:[]},{name:'三级',data:[]},{name:'四级',data:[]}];
                            
                            newArr.forEach((item,index)=>{
                                    item.type= 'bar';
                                    item.stack='总量';
                                    item.itemStyle={};
                                    item.itemStyle.barBorderRadius=4;
                                    item.itemStyle.borderColor='#fff';
                                for(var i=0; i<xData.length; i++){
                                    if(data.data.filterProperty("Drug",xData[i]).filterProperty("Grade",item.name).length>0){
                                        newArr[index].data.push(data.data.filterProperty("Drug",xData[i]).filterProperty("Grade",item.name)[0].Counter);
                                    }else{
                                        newArr[index].data.push(0);
                                    }
                                }                            
                            })
                            self.option.xAxis.data=xData;
                            self.option.series=newArr;
                            self.$refs.case.hideLoading();
                        }else{
                            self.$refs.case.hideLoading();
                            self.nodata=true;
                        }
                        
                    }
                }
            })
        }
    }
};
</script>