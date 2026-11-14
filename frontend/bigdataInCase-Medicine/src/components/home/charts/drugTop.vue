<template>
  <div class="drug-top chart">
    <div class="case-title">Top10药品销额情况图表</div>
    <echart theme="med" class="case-chart" :options="option" />
  </div>
</template>
<script>
import Vue from "vue";
import ECharts from "vue-echarts";
import "echarts/lib/component/tooltip";
import "echarts/lib/chart/custom";
export default {
  components: {
    echart: ECharts,
  },
  data() {
    return {
      data: [
        [10, 16, 3, "A"],
        [16, 18, 15, "B"],
        [18, 26, 12, "C"],
        [26, 32, 22, "D"],
        [32, 56, 7, "E"],
        [56, 62, 17, "F"],
      ],
      colorList: [
        "#1F6F5C",
        "#267A62",
        "#2D8568",
        "#34906E",
        "#3B9B74",
        "#42A67A",
        "#49B180",
        "#50BC86",
        "#57C78C",
        "#5ED292",
      ],
      option: {
        grid: {
          top: 10,
          bottom: 0,
          left: 0,
          right: 0,
        },
        tooltip: {},
        xAxis: {
          scale: true,
          axisTick: {
            show: true,
          },
          axisLine: {
            show: false,
          },
          axisLabel: {
            show: true,
          },
          splitLine: {
            show: false,
          },
        },
        yAxis: {
          axisTick: {
            show: false,
          },
          axisLine: {
            show: false,
          },
          axisLabel: {
            show: false,
          },
          splitLine: {
            show: false,
          },
        },
        series: [
          {
            type: "custom",
            renderItem: this.renderItem,
            label: {
              normal: {
                show: true,
                position: "top",
              },
            },
            dimensions: ["销额", "销量", "销额"],
            encode: {
              x: [0, 1],
              y: 2,
              tooltip: [2, 1],
              itemName: 3,
            },
            data: [],
          },
        ],
      },
    };
  },
  mounted: function () {
    this.getSeries();
  },
  methods: {
    getSeries: function () {
      var self = this;
      Vue.ajax.send({
        url: "/home/top10",
        data: {},
        success: function (data) {
          if (!!data && data.code == "200") {
            self.data = [];
            var startX = 0;
            data.data.forEach((item, index) => {
              self.data.push([
                startX,
                item.Counter,
                Math.round(item.Amount),
                item.Name,
              ]);
              startX = startX + item.Counter;
            });
            self.newData();
          }
        },
      });
    },
    renderItem: function (params, api) {
      var yValue = api.value(2);
      var start = api.coord([api.value(0), yValue]);
      var size = api.size([api.value(1), yValue]);
      var style = api.style();

      return {
        type: "rect",
        shape: {
          x: start[0],
          y: start[1],
          width: size[0],
          height: size[1],
        },
        style: style,
      };
    },
    newData: function () {
      var data1 = [];
      this.data.forEach((item, index) => {
        data1.push({
          value: item,
          itemStyle: {
            normal: {
              color: this.colorList[index],
            },
          },
        });
      });
      this.option.series[0].data = data1;
    },
  },
};
</script>