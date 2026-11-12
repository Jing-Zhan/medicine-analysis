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
import 'echarts/lib/chart/pie'
import 'echarts/lib/component/legend'
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
            color:['#6ecbbc','#7bb6ef','#f7a25a','#b5a2de','#de7984','#5fccc3','#e7d352'],
            tooltip: {
                trigger: 'item',
                formatter: '{b}：{c} ({d}%)'
            },
            legend: {
                orient: 'vertical',
                right: 10,
                top: 'middle',
                textStyle:{
                    color:'#364554'
                }
            },
            series: [{
                type: 'pie',
                radius: ['38%', '68%'],
                center: ['38%', '56%'],
                avoidLabelOverlap: true,
                label: {
                    normal: {
                        formatter: '{b}\n{d}%',
                        color:'#364554'
                    }
                },
                data: []
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
                             var pieData=[];
                             data.data.forEach(element => {
                                 pieData.push({
                                     name: element.SectionName,
                                     value: element.Counter
                                 });
                             });
                            self.option.series[0].data=pieData;
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
