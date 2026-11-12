/* =========================================================================
 * 药品适应症数据大屏 —— 5 张图
 * 依赖：echarts.min.js(4.x) + china.js（都用素材包里自带的）
 * 数据：/api/province/ /api/drug-top10/ /api/drug-amount/ /api/disease-top10/ /api/relations/
 * ========================================================================= */
(function () {
    'use strict';

    var API = {
        province: '/api/province/',
        drugTop: '/api/drug-top10/',
        drugAmount: '/api/drug-amount/',
        disease: '/api/disease-top10/',
        relations: '/api/relations/'
    };

    var charts = {};
    var demoFlag = false;
    var AXIS_COLOR = '#9cc9ee';
    var SPLIT_COLOR = 'rgba(120,180,240,0.12)';

    /* ------------------------------------------------------------ 工具函数 */
    function $(id) { return document.getElementById(id); }

    function getJSON(url) {
        return fetch(url, { credentials: 'same-origin' }).then(function (r) {
            if (!r.ok) { throw new Error(url + ' -> HTTP ' + r.status); }
            return r.json();
        });
    }

    function fmtInt(n) {
        n = Number(n || 0);
        if (n >= 100000000) { return (n / 100000000).toFixed(2) + '亿'; }
        if (n >= 10000) { return (n / 10000).toFixed(1) + '万'; }
        return n.toLocaleString();
    }

    function fmtMoney(n) {
        n = Number(n || 0);
        if (n >= 100000000) { return (n / 100000000).toFixed(2) + '亿元'; }
        if (n >= 10000) { return (n / 10000).toFixed(1) + '万元'; }
        return n.toFixed(2) + '元';
    }

    function cut(s, n) {
        s = String(s == null ? '' : s);
        return s.length > n ? s.slice(0, n - 1) + '…' : s;
    }

    function initChart(id) {
        var el = $(id);
        if (!el) { return null; }
        var c = echarts.init(el);
        charts[id] = c;
        return c;
    }

    function showError(id, msg) {
        var el = $(id);
        if (!el) { return; }
        el.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;'
            + 'color:#ff8a8a;font-size:13px;text-align:center;padding:8px;">' + msg + '</div>';
    }

    /* --------------------------------------------------------------- 时钟 */
    function tickClock() {
        var d = new Date();
        var p = function (v) { return v < 10 ? '0' + v : '' + v; };
        var now = d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate())
            + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds());
        $('currentTime').innerHTML = now + '<br/><span style="color:#7fa8cf;">'
            + (demoFlag ? '⚠ 演示数据（未连上 MySQL）' : '● MySQL 实时数据') + '</span>';
    }

    /* ------------------------------------------------------- 1. 省份地图 */
    var geoCoordMap = {};

    function buildGeoCoord() {
        try {
            var mapObj = echarts.getMap('china');
            if (!mapObj || !mapObj.geoJson) { return false; }
            mapObj.geoJson.features.forEach(function (f) {
                if (f.properties && f.properties.name) {
                    geoCoordMap[f.properties.name] = f.properties.cp;
                }
            });
            return true;
        } catch (e) {
            return false;
        }
    }

    function renderProvince(payload) {
        var chart = charts.data_province || initChart('data_province');
        var rows = (payload && payload.data) || [];
        if (!rows.length) { showError('data_province', '暂无省份数据'); return; }

        var byName = {};
        rows.forEach(function (r) { byName[r.short || r.name] = r; });

        var casesData = rows.map(function (r) { return { name: r.short || r.name, value: r.cases || 0 }; });
        var maxCases = Math.max.apply(null, casesData.map(function (d) { return d.value; }).concat([1]));
        var maxAmount = Math.max.apply(null, rows.map(function (r) { return r.amount || 0; }).concat([1]));

        // 金额用散点大小表达，经纬度来自 china.js
        var scatterData = rows.map(function (r) {
            var cp = geoCoordMap[r.short || r.name];
            if (!cp) { return null; }
            var size = 8 + Math.sqrt((r.amount || 0) / maxAmount) * 26;
            return { name: r.short || r.name, value: cp.concat([size]) };
        }).filter(Boolean);

        chart.setOption({
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(6,20,38,0.92)',
                borderColor: 'rgba(7,166,255,0.7)',
                textStyle: { color: '#eaf6ff', fontSize: 12 },
                formatter: function (p) {
                    var d = byName[p.name] || {};
                    return '<b style="color:#37c2ff">' + (d.name || p.name) + '</b><br/>'
                        + '病例数：<span style="color:#4be08a">' + fmtInt(d.cases) + '</span><br/>'
                        + '用药金额：<span style="color:#ffd166">' + fmtMoney(d.amount) + '</span>';
                }
            },
            visualMap: {
                show: true,
                min: 0,
                max: maxCases,
                left: '3%',
                bottom: '4%',
                calculable: true,
                seriesIndex: [0],
                text: ['高', '低'],
                textStyle: { color: AXIS_COLOR, fontSize: 11 },
                inRange: { color: ['#0a2f57', '#1f6fae', '#37c2ff'] }
            },
            geo: {
                map: 'china',
                roam: true,
                zoom: 1.15,
                label: { normal: { show: false }, emphasis: { show: false } },
                itemStyle: {
                    normal: { areaColor: '#0b2a4a', borderColor: '#2f6fb0', borderWidth: 0.8 },
                    emphasis: { areaColor: '#1c5c92' }
                }
            },
            series: [
                {
                    name: '病例数',
                    type: 'map',
                    map: 'china',
                    geoIndex: 0,
                    data: casesData,
                    label: { normal: { show: false }, emphasis: { show: true, color: '#fff' } }
                },
                {
                    name: '用药金额',
                    type: 'effectScatter',
                    coordinateSystem: 'geo',
                    data: scatterData,
                    symbolSize: function (val) { return val[2]; },
                    rippleEffect: { period: 5, brushType: 'stroke', scale: 3 },
                    itemStyle: { normal: { color: '#ffd166', shadowBlur: 8, shadowColor: '#ffd166' } },
                    tooltip: { show: false },
                    zlevel: 1
                }
            ]
        }, true);
    }

    /* --------------------------------------------- 2. 用药 TOP10（横向柱） */
    function renderDrugTop(payload) {
        var chart = charts.drug1 || initChart('drug1');
        var rows = ((payload && payload.data) || []).slice(0, 10).reverse();
        if (!rows.length) { showError('drug1', '暂无用药数据'); return; }

        chart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                backgroundColor: 'rgba(6,20,38,0.92)',
                borderColor: 'rgba(7,166,255,0.7)',
                textStyle: { color: '#eaf6ff', fontSize: 12 },
                formatter: function (p) {
                    return p[0].name + '<br/>处方数：' + fmtInt(p[0].value);
                }
            },
            grid: { left: 6, right: 46, top: 10, bottom: 6, containLabel: true },
            xAxis: {
                type: 'value',
                axisLabel: { color: AXIS_COLOR, fontSize: 10 },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { lineStyle: { color: SPLIT_COLOR } }
            },
            yAxis: {
                type: 'category',
                data: rows.map(function (r) { return cut(r.name, 12); }),
                axisLabel: { color: '#cfe6ff', fontSize: 11 },
                axisLine: { lineStyle: { color: 'rgba(47,111,176,0.6)' } },
                axisTick: { show: false }
            },
            series: [{
                type: 'bar',
                data: rows.map(function (r) { return r.value; }),
                barWidth: '58%',
                itemStyle: {
                    normal: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#1b6ca8' },
                            { offset: 1, color: '#7fe3ff' }
                        ])
                    }
                },
                label: {
                    normal: {
                        show: true, position: 'right', color: AXIS_COLOR, fontSize: 10,
                        formatter: function (p) { return fmtInt(p.value); }
                    }
                }
            }]
        }, true);
    }

    /* --------------------------------------- 3. 用药分布 TOP10（环形饼图） */
    function renderDrugAmount(payload) {
        var chart = charts.drug2 || initChart('drug2');
        var rows = ((payload && payload.data) || []).slice(0, 10);
        if (!rows.length) { showError('drug2', '暂无金额数据'); return; }

        chart.setOption({
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(6,20,38,0.92)',
                borderColor: 'rgba(7,166,255,0.7)',
                textStyle: { color: '#eaf6ff', fontSize: 12 },
                formatter: function (p) {
                    return p.name + '<br/>金额：' + fmtMoney(p.value) + '<br/>占比：' + p.percent + '%';
                }
            },
            color: ['#37c2ff', '#4be08a', '#ffd166', '#ff8a65', '#b388ff',
                    '#40c4ff', '#69f0ae', '#ffab40', '#ff5252', '#18ffff'],
            series: [{
                type: 'pie',
                radius: ['38%', '62%'],
                center: ['50%', '52%'],
                avoidLabelOverlap: true,
                itemStyle: { normal: { borderColor: '#0a1c33', borderWidth: 1 } },
                label: {
                    normal: {
                        show: true,
                        color: '#cfe6ff',
                        fontSize: 10,
                        formatter: function (p) { return cut(p.name, 8) + '\n' + p.percent + '%'; }
                    }
                },
                labelLine: { normal: { length: 6, length2: 6, lineStyle: { color: 'rgba(120,180,240,0.6)' } } },
                data: rows.map(function (r) { return { name: r.name, value: r.value }; })
            }]
        }, true);
    }

    /* ------------------------------------------------ 4. 病症 TOP10（柱） */
    function renderDisease(payload) {
        var chart = charts.data_diseases || initChart('data_diseases');
        var rows = ((payload && payload.data) || []).slice(0, 10).reverse();
        if (!rows.length) { showError('data_diseases', '暂无病症数据'); return; }

        chart.setOption({
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                backgroundColor: 'rgba(6,20,38,0.92)',
                borderColor: 'rgba(7,166,255,0.7)',
                textStyle: { color: '#eaf6ff', fontSize: 12 },
                formatter: function (p) { return p[0].name + '<br/>出现次数：' + fmtInt(p[0].value); }
            },
            grid: { left: 6, right: 46, top: 10, bottom: 6, containLabel: true },
            xAxis: {
                type: 'value',
                axisLabel: { color: AXIS_COLOR, fontSize: 10 },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { lineStyle: { color: SPLIT_COLOR } }
            },
            yAxis: {
                type: 'category',
                data: rows.map(function (r) { return cut(r.name, 11); }),
                axisLabel: { color: '#cfe6ff', fontSize: 11 },
                axisLine: { lineStyle: { color: 'rgba(47,111,176,0.6)' } },
                axisTick: { show: false }
            },
            series: [{
                type: 'bar',
                data: rows.map(function (r) { return r.value; }),
                barWidth: '58%',
                itemStyle: {
                    normal: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                            { offset: 0, color: '#12558f' },
                            { offset: 1, color: '#69f0ae' }
                        ])
                    }
                },
                label: {
                    normal: {
                        show: true, position: 'right', color: AXIS_COLOR, fontSize: 10,
                        formatter: function (p) { return fmtInt(p.value); }
                    }
                }
            }]
        }, true);
    }

    /* ------------------------------------------ 5. 药物关联（环形关系图） */
    function renderRelations(payload) {
        var chart = charts.data_apliori || initChart('data_apliori');
        var nodes = (payload && payload.nodes) || [];
        var links = (payload && payload.links) || [];
        if (!nodes.length || !links.length) {
            showError('data_apliori', '暂无关联数据<br/>（先跑任务24生成 rules_data.csv）');
            return;
        }

        var palette = ['#37c2ff', '#4be08a', '#ffd166', '#ff8a65', '#b388ff',
                       '#40c4ff', '#69f0ae', '#ffab40', '#ff5252', '#18ffff', '#ea80fc', '#a7ffeb'];

        var maxConf = Math.max.apply(null, links.map(function (l) { return l.confidence || 0; }).concat([1]));

        chart.setOption({
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(6,20,38,0.92)',
                borderColor: 'rgba(7,166,255,0.7)',
                textStyle: { color: '#eaf6ff', fontSize: 12 },
                formatter: function (p) {
                    if (p.dataType === 'edge') {
                        return p.data.source + ' → ' + p.data.target
                            + '<br/>置信度：' + Number(p.data.confidence).toFixed(3)
                            + '<br/>提升度：' + Number(p.data.lift).toFixed(2);
                    }
                    return p.name + '<br/>关联药品数：' + p.value;
                }
            },
            series: [{
                type: 'graph',
                layout: 'circular',
                circular: { rotateLabel: true },
                roam: true,
                symbolSize: function (val) { return 10 + Math.min(val || 1, 8) * 2.2; },
                label: {
                    normal: {
                        show: true,
                        position: 'right',
                        color: '#cfe6ff',
                        fontSize: 10,
                        formatter: function (p) { return cut(p.name, 9); }
                    }
                },
                itemStyle: { normal: { borderColor: '#0a1c33', borderWidth: 1 } },
                lineStyle: { normal: { opacity: 0.55, curveness: 0.3 } },
                emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
                data: nodes.map(function (n, i) {
                    return {
                        name: n.name,
                        value: n.value,
                        itemStyle: { normal: { color: palette[i % palette.length] } }
                    };
                }),
                links: links.map(function (l) {
                    return {
                        source: l.source,
                        target: l.target,
                        value: l.confidence,
                        confidence: l.confidence,
                        lift: l.lift,
                        lineStyle: {
                            normal: {
                                width: 1 + (l.confidence / maxConf) * 3,
                                color: 'source',
                                curveness: 0.3,
                                opacity: 0.55
                            }
                        }
                    };
                })
            }]
        }, true);
    }

    /* ------------------------------------------------------------ 加载 */
    function markDemo(payload) {
        if (payload && payload.source === 'demo') { demoFlag = true; }
    }

    function loadAll() {
        if (!buildGeoCoord()) {
            showError('data_province', '地图未注册<br/>请检查 static/js/china.js 是否加载');
        }

        getJSON(API.province).then(function (d) { markDemo(d); renderProvince(d); })
            .catch(function (e) { showError('data_province', '加载失败：' + e.message); });

        getJSON(API.drugTop).then(function (d) { markDemo(d); renderDrugTop(d); })
            .catch(function (e) { showError('drug1', '加载失败：' + e.message); });

        getJSON(API.drugAmount).then(function (d) { markDemo(d); renderDrugAmount(d); })
            .catch(function (e) { showError('drug2', '加载失败：' + e.message); });

        getJSON(API.disease).then(function (d) { markDemo(d); renderDisease(d); })
            .catch(function (e) { showError('data_diseases', '加载失败：' + e.message); });

        getJSON(API.relations).then(function (d) { markDemo(d); renderRelations(d); })
            .catch(function (e) { showError('data_apliori', '加载失败：' + e.message); });

        if ($('dataSource')) {
            $('dataSource').innerText = '数据来源：yiyao · prescription_diseases';
        }
        tickClock();
    }

    window.addEventListener('resize', function () {
        Object.keys(charts).forEach(function (k) { charts[k].resize(); });
    });

    // 时钟每秒走，数据每 5 分钟刷新一次
    setInterval(tickClock, 1000);
    loadAll();
    setInterval(loadAll, 5 * 60 * 1000);
})();
