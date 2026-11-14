<template>
   <div class="drug-top chart">
        <div class="case-title">Top10药品销额情况图表</div>
        <!-- <echart theme="med" class="case-chart" :options="option"/> -->
        <div class="case-chart" id="drugTop"></div>
    </div>
</template>
<script>
import Vue from 'vue'
import echarts from  '../../../../static/echarts.min.js'
export default {
  // components: {
  //       echart:ECharts
  // },
  data() {
    return {
        
    };
  },
  mounted: function() {
     
      this.showChart();
      // this.getSeries();
    },
    methods: {
        getSeries: function(){
            var self = this;
            Vue.ajax.send({
                url: "/home/top10",
                data: {},
                success: function(data) {
                    if (!!data && data.code=='200') {      
                        //self.option.series[0].data=data.result;
                    }
                }
            }); 
        },
        renderItem:function(params, api){
            var yValue = api.value(2);
            var start = api.coord([api.value(0), yValue]);
            var size = api.size([api.value(1) - api.value(0), yValue]);
            var style = api.style();

            return {
                type: 'rect',
                shape: {
                    x: start[0],
                    y: start[1],
                    width: size[0],
                    height: size[1]
                },
                style: style
            };
        },
        // newData:function(){
        //     this.data = echarts.util.map(this.data, function (item, index) {
        //         return {
        //             value: item,
        //             itemStyle: {
        //                 normal: {
        //                     color: this.colorList[index]
        //                 }
        //             }
        //         };
        //     });
        //   this.option.series[0].data=this.data;
        // },
        showChart:function(){
            var data = [[10, 16, 3, 'A'], [16, 18, 15, 'B'], [18, 26, 12, 'C'], [26, 32, 22, 'D'], [32, 56, 7, 'E'], [56, 62, 17, 'F']];
            var colorList = ['#4f81bd', '#c0504d', '#9bbb59', '#604a7b', '#948a54', '#e46c0b'];

            data = echarts.util.map(data, function (item, index) {
                return {
                    value: item,
                    itemStyle: {
                        normal: {
                            color: colorList[index]
                        }
                    }
                };
            });
            var option = {
                tooltip: {
                },
                xAxis: {
                    scale: true
                },
                yAxis: {
                },
                series: [{
                    type: 'custom',
                    renderItem: this.renderItem,
                    label: {
                        normal: {
                            show: true,
                            position: 'top'
                        }
                    },
                    dimensions: ['from', 'to', 'profit'],
                    encode: {
                        x: [0, 1],
                        y: 2,
                        tooltip: [0, 1, 2],
                        itemName: 3
                    },
                    data: data
                }]
            };
            var drugTop = echarts.init(document.getElementById('drugTop'));
                drugTop.setOption(option);  
        }
    }
};
</script>
<style scoped>
</style>