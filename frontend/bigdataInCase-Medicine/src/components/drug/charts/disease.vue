<template>
    <div class="diseases chart">
        <div class="case-title">目标药品对应适应症</div>
        <echart theme="med" ref="case" class="case-chart" :options="option"/>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/sunburst'
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
        colors:['#6B7FD7','#D9695F','#C9A227','#2FA98C','#2E7DD1','#57B87F','#CF8A2C','#ae7146','#7FD3C7','#eb6465','83b5e6','#424149'],
        option:{
            color:['#6B7FD7','#D9695F','#C9A227','#2FA98C','#2E7DD1','#57B87F','#CF8A2C','#ae7146','#7FD3C7','#eb6465','83b5e6','#424149'],            
            tooltip: {},
            series: {
                type: 'sunburst',
                highlightPolicy: 'ancestor',
                data: [],
                radius: [0, '95%'],
                sort: null,
                levels: [{}, {
                    r0: '15%',
                    r: '55%',
                    itemStyle: {
                        borderWidth: 2
                    },
                    label: {
                        align: 'left'
                    }
                }, {
                    r0: '55%',
                    r: '100%',
                    label: {
                        align: 'right'
                    }
                }]
            }
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
                url: "/drug/diseases?keyword="+self.keyword,
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {  
                        if(data.data.length>0){
                            var newArr=[];
                            data.data.forEach((item,index)=>{
                                if(newArr.someProperty("name",item.Drug)){
                                    var drug=newArr.findProperty("name",item.Drug);
                                    if(drug["children"].someProperty("name",item.Disease)){
                                        drug["children"].findProperty("name",item.Disease.slice(0,8)).push({"value":item.Counter});
                                    }
                                    else{
                                        drug["children"].push({"name":item.Disease.slice(0,8),"value":item.Counter});
                                    }
                                }
                                else{
                                    newArr.push({"name":item.Drug.slice(0,8),"children":[{"name":item.Disease.slice(0,8),"value":item.Counter}]});
                                }
                            })
                            self.option.series.data=newArr;
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