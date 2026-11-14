/**
 * ECharts 统一主题
 * ============================================================
 * 图表原来各自写死的配色偏淡，坐标轴文字用 #b8cde3 落在白色卡片上
 * 对比度不足，12 张图放在一起也不像一套。这里定义一份主题，
 * 在 main.js 里注册成 med，各图表用 theme="med" 引用。
 *
 * 主题只负责坐标轴、网格线、图例、提示框与默认色板；
 * 各图表仍然可以用自己的 option 覆盖单项。
 */
export default {
    color: ['#1f6f5c', '#2e7dd1', '#b4802f', '#6b7fd7', '#2fa98c', '#d9695f', '#8a97a2'],
    backgroundColor: 'transparent',
    // 一页 12 张图，进页面时逐条播放动画会拖慢首屏，直接渲染更稳
    animation: false,
    textStyle: {
        fontFamily: '微软雅黑, Microsoft YaHei, sans-serif',
        color: '#43535f'
    },
    title: {
        textStyle: {
            color: '#16232e',
            fontWeight: 700,
            fontSize: 15
        },
        subtextStyle: {
            color: '#74838e',
            fontSize: 12
        }
    },
    legend: {
        textStyle: {
            color: '#43535f',
            fontSize: 12
        },
        itemWidth: 10,
        itemHeight: 10,
        itemGap: 14
    },
    tooltip: {
        backgroundColor: 'rgba(255, 255, 255, .98)',
        borderColor: '#d3dce3',
        borderWidth: 1,
        padding: [8, 12],
        textStyle: {
            color: '#16232e',
            fontSize: 12.5
        },
        extraCssText: 'box-shadow: 0 10px 26px rgba(22,35,46,.14); border-radius: 10px;'
    },
    grid: {
        containLabel: true,
        left: 12,
        right: 18,
        top: 44,
        bottom: 8
    },
    categoryAxis: {
        axisLine: {
            show: true,
            lineStyle: { color: '#dfe6eb' }
        },
        axisTick: { show: false },
        axisLabel: {
            color: '#6e7b87',
            fontSize: 12
        },
        splitLine: {
            show: false
        }
    },
    valueAxis: {
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
            color: '#6e7b87',
            fontSize: 12
        },
        splitLine: {
            show: true,
            lineStyle: {
                color: '#eef2f5',
                type: 'dashed'
            }
        }
    },
    line: {
        symbolSize: 6,
        smooth: true,
        lineStyle: { width: 2 }
    },
    bar: {
        itemStyle: {
            barBorderRadius: [6, 6, 0, 0]
        }
    },
    pie: {
        itemStyle: {
            borderColor: '#fff',
            borderWidth: 2
        }
    }
}
