<template>
    <div class="union chart">
        <div class="case-title">目标适应症联合用药分析</div>
        <div class="case-chart" id="union"></div>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import '../../../../static/echarts-all.js'
export default {
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
                color : [
                    '#FBB367','#80B1D2','#FB8070','#CC99FF','#B0D961',
                    '#99CCCC','#BEBBD8','#FFCC99','#8DD3C8','#FF9999',
                    '#CCEAC4','#BB81BC','#FBCCEC','#CCFF66','#99CC66',
                    '#66CC66','#FF6666','#FFED6F','#ff7f50','#87cefa',
                ],                
                 tooltip : {
                    trigger: 'item',
                    formatter: function (params) {
                        if (params.indicator2) {    // is edge
                            return params.indicator2 + ' ' + params.name + ' ' + params.indicator;
                        } else {    // is node
                            return params.name
                        }
                    }
                },                
                series : [
                {
                    type:'chord',
                    sort : 'ascending',
                    sortSub : 'descending',
                    showScale : false,
                    itemStyle : {
                        normal : {
                            label : {
                                rotate : true
                            }
                        }
                    },
                    // 使用 nodes links 表达和弦图
                    nodes: [],
                    links: []
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
            echarts2.init(document.getElementById('union')).showLoading({
                text: '',
                effect: 'spin'
            })
            self.nodata=false;
            Vue.ajax.send({
                url: "/disease/drug?keyword="+this.keyword,
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {
                        if(data.data.Links&&data.data.Links.length>0&&data.data.Links!=null){
                            self.option.series[0].nodes=data.data.Nodes;
                            self.option.series[0].links=data.data.Links;
                            var union = echarts2.init(document.getElementById('union')).setOption(self.option);
                        }else{
                            self.nodata=true;
                        }  
                        
                    }
                }
            }); 
        },
        showChart:function(){
        }
    }
};
</script>