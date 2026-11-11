<template>
    <div class="group chart">
        <div class="case-title">目标适应症用药组合分析</div>
        <echart ref="case" class="case-chart" :options="option"/>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/tree'
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
            tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
            },
            series: [
                {
                    type: 'tree',
                    data: [],
                    top: '1%',
                    left: '7%',
                    bottom: '1%',
                    right: '20%',
                    symbolSize: 7,
                    label: {
                        normal: {
                            position: 'left',
                            verticalAlign: 'middle',
                            align: 'right',
                            fontSize: 9
                        }
                    },
                    leaves: {
                        label: {
                            normal: {
                                position: 'right',
                                verticalAlign: 'middle',
                                align: 'left'
                            }
                        }
                    },
                    expandAndCollapse: true,
                    animationDuration: 550,
                    animationDurationUpdate: 750
                }
            ]
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
                url: "/disease/union?keyword="+this.keyword,
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {
                        if(data.data.length>0){
                            var xData=[];
                            data.data.forEach((item,index)=>{
                                xData.push(item.DiseaseName);
                            })
                            xData=xData.distinct();
                            var newArr=[];
                            data.data.forEach((item,index)=>{
                                if(newArr.someProperty("name",item.DiseaseName)){
                                    var Disease=newArr.findProperty("name",item.DiseaseName);
                                    if(Disease["children"].someProperty("name",item.DrugName)){
                                        Disease["children"].findProperty("name",item.DrugName).push({"value":item.DrugCount});
                                    }
                                    else{
                                        Disease["children"].push({"name":item.DrugName,"value":item.DrugCount});
                                    }
                                }
                                else{
                                    newArr.push({"name":item.DiseaseName,"children":[{"name":item.DrugName,"value":item.DrugCount}]});
                                }
                            });
                            var data1=[{name:'适应症用药',children:newArr}];
                            self.option.series[0].data=data1;
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