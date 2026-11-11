<template>
    <div class="section chart">
        <div class="case-title">目标药品科室分布</div>
        <echart ref="case" class="case-chart" :options="option"/>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import 'echarts/lib/chart/treemap'
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
            color:['#29c7ce','#b5a2de','#5ab2ef','#ffba84','#8c9ab5','#e7cf08'],
            tooltip: {                
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c}"
            },
            tooltip: {
                formatter: function (info) {
                    var value = info.value;
                    var treePathInfo = info.treePathInfo;
                    var treePath = [];
                    for (var i = 1; i < treePathInfo.length; i++) {
                        treePath.push(treePathInfo[i].name);
                    }
                    return [
                        treePath[0]+'<br>' + treePath[1] + ': '+value
                    ];
                }
            },
            series: [{
                type: 'treemap',
                label:{
                    color:'#16190d'
                },
                breadcrumb:false,
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
                url: "/drug/section?keyword="+self.keyword,
                data: {},
                success: function(data) {
                     if (!!data && data.code=='200') {  
                        if(data.data.length>0){
                            let newArr=new Array();
                            data.data.forEach(item=>{
                                if(newArr.someProperty("name",item.Drug)){
                                    var drug=newArr.findProperty("name",item.Drug);
                                    if(drug["children"].someProperty("name",item.Section)){
                                        drug["children"].findProperty("name",item.Section).push({"value":item.Counter});
                                    }
                                    else{
                                        drug["children"].push({"name":item.Section,"value":item.Counter});
                                    }
                                }
                                else{
                                    newArr.push({"name":item.Drug,"children":[{"name":item.Section,"value":item.Counter}]});
                                }
                            })
                            self.option.series[0].data=newArr;    
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