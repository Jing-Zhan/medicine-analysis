<template>
    <div class="city chart">
        <div class="case-title">药品品牌覆盖城市图</div>
        <echart ref="case" class="case-chart" :options="option"  autoresize/>
        <div class="nodata" v-show="nodata">暂无数据</div>
    </div>
</template>
<script>
import Vue from 'vue'
import ECharts from 'vue-echarts'
import geoCoordMap from 'echarts/map/json/china-cities.json'
import mapStyle from '../../../../static/mapStyle.json'
import 'echarts/lib/chart/scatter'
import 'echarts/lib/chart/effectScatter'
import 'echarts/lib/chart/map'
import 'echarts/map/js/world'
import 'echarts/map/js/china'
import chinaMap from 'echarts/map/json/china'
import 'echarts/extension/bmap/bmap'
import 'echarts/extension/dataTool/index'
// registering map data
ECharts.registerMap('china', chinaMap)
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
            tooltip : {
                trigger: 'item',
                formatter: function (params, ticket, callback) {
                    return params.name+'：'+params.value[2]
                }
            },
            bmap: {
                center: [120.33,36.07],
                zoom: 7,
                roam: true,
                mapStyle: mapStyle
            },
            series : [
                {
                    name: '人参药酒药品覆盖城市',
                    type: 'scatter',
                    coordinateSystem: 'bmap',
                    data:[],
                    symbolSize:14,
                    // symbolSize: function (val) {
                    //     return Math.sqrt(val[2]);                        
                    // },
                    label: {
                        normal: {
                            formatter: '{b}',
                            position: 'right',
                            show: false,                            
                        },
                        emphasis: {
                            show: true,
                            color:'#000000'
                        }
                    },
                    itemStyle: {
                        normal: {
                            color: '#3085fe',
                            opacity:1
                        }
                    }
                }
            ]
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
                            self.option.series[0].data=self.convertData(data.data);
                            self.$refs.case.hideLoading();
                        }else{
                            self.$refs.case.hideLoading();
                            self.nodata=true;
                        }
                     }                    
                }
            }); 
        },
        convertData:function (data) {
            var res = [];
                
            var newArr=[];
            geoCoordMap.features.forEach(element => {
                newArr.push(element.properties)
            });
            for (var i = 0; i < data.length; i++) {
                var geoCoord='';
                if(data[i].Name.indexOf('市')>0){
                    geoCoord = newArr.findProperty('name',data[i].Name.replace('市','')).cp;
                }else if(newArr.findProperty('name',data[i].Name)){
                    geoCoord = newArr.findProperty('name',data[i].Name).cp;
                }             
                if (geoCoord) {
                    res.push({
                        name: data[i].Name,
                        value: geoCoord.concat(data[i].Counter)
                    });
                }
            }
            return res;
        }
    }
};
</script>