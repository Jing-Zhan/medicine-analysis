/**
 * 前端假数据（模拟 12 个后端接口的返回）
 * ============================================================
 * 接口还没通，图表先用这里的数据渲染；后端接口通了以后把
 * src/config.js 里的 useMock 改成 false 即可，组件代码不用动。
 *
 * 每个 key 是接口路径（不含 ?keyword= 查询串），value 是返回数据工厂函数：
 *     (keyword) => ({ code: '200', data: ... })
 * 返回结构必须和组件里 success 回调取字段的方式一致。
 */

/* ---------------------------- 基础名录 ---------------------------- */

// 首页概览数字卡片
const overview = () => ({
    code: '200',
    data: [
        { label: '总销售额（万元）', value: 1286540, unit: '' },
        { label: '总销量（件）', value: 86240, unit: '' },
        { label: '覆盖城市', value: 328, unit: '个' },
        { label: '覆盖医院', value: 12650, unit: '家' },
        { label: '覆盖适应症', value: 1024, unit: '种' },
        { label: '收录药品', value: 3860, unit: '种' }
    ]
});

// 城市等级竞争：柱状图（销额）+ 折线（增长率）
const cityLevel = () => ({
    code: '200',
    data: {
        YearData: ['2016', '2017', '2018', '2019', '2020', '2021'],
        CityData: [
            { Level: '一线城市', BarData: [1250, 1380, 1520, 1690, 1840, 2030], LineData: [12.5, 10.4, 10.1, 11.2, 8.9, 10.3] },
            { Level: '二线城市', BarData: [980, 1105, 1240, 1330, 1470, 1615], LineData: [9.8, 12.8, 12.2, 7.3, 10.5, 9.9] },
            { Level: '三线城市', BarData: [760, 845, 915, 1020, 1145, 1260], LineData: [8.2, 11.2, 8.3, 11.5, 12.3, 10.0] },
            { Level: '四线及以下', BarData: [430, 480, 540, 595, 650, 720], LineData: [6.5, 11.6, 12.5, 10.2, 9.2, 10.8] }
        ]
    }
});

// 不同年龄患病比例：男 / 女 柱状图
const age = () => ({
    code: '200',
    data: {
        AgeRange: ['0-3岁', '3-6岁', '6-12岁', '12-20岁', '20-30岁', '30-40岁', '40-50岁', '50-60岁', '60-70岁', '70岁+'],
        AgeData: [
            [120, 260, 540, 980, 1860, 2140, 1760, 1520, 980, 540],
            [110, 240, 500, 1020, 2240, 2380, 1890, 1640, 1120, 660]
        ]
    }
});

// 销额 Top10 药品：[{ Name, Amount（万元）, Counter（销量） }]
const top10 = () => ({
    code: '200',
    data: [
        { Name: '阿莫西林胶囊', Amount: 96, Counter: 1280 },
        { Name: '头孢克肟分散片', Amount: 88, Counter: 1140 },
        { Name: '复方丹参滴丸', Amount: 81, Counter: 1020 },
        { Name: '布洛芬缓释胶囊', Amount: 74, Counter: 960 },
        { Name: '奥美拉唑肠溶胶囊', Amount: 68, Counter: 900 },
        { Name: '氯雷他定片', Amount: 62, Counter: 840 },
        { Name: '缬沙坦胶囊', Amount: 57, Counter: 790 },
        { Name: '二甲双胍缓释片', Amount: 52, Counter: 730 },
        { Name: '瑞舒伐他汀钙片', Amount: 46, Counter: 660 },
        { Name: '蒙脱石散', Amount: 41, Counter: 600 }
    ]
});

// 各省份增长格局：[{ Name, Amount（销额）, Counter（销量） }]
const province = () => ({
    code: '200',
    data: [
        { Name: '广东省', Amount: 320, Counter: 210 },
        { Name: '江苏省', Amount: 302, Counter: 190 },
        { Name: '山东省', Amount: 301, Counter: 186 },
        { Name: '浙江省', Amount: 334, Counter: 204 },
        { Name: '河南省', Amount: 390, Counter: 232 },
        { Name: '四川省', Amount: 286, Counter: 172 },
        { Name: '湖北省', Amount: 265, Counter: 158 },
        { Name: '湖南省', Amount: 248, Counter: 149 },
        { Name: '河北省', Amount: 236, Counter: 141 },
        { Name: '福建省', Amount: 224, Counter: 134 },
        { Name: '安徽省', Amount: 212, Counter: 127 },
        { Name: '上海市', Amount: 260, Counter: 156 },
        { Name: '北京市', Amount: 254, Counter: 152 },
        { Name: '辽宁省', Amount: 186, Counter: 112 },
        { Name: '陕西省', Amount: 174, Counter: 104 },
        { Name: '江西省', Amount: 162, Counter: 97 },
        { Name: '重庆市', Amount: 158, Counter: 95 },
        { Name: '广西壮族自治区', Amount: 146, Counter: 88 },
        { Name: '山西省', Amount: 132, Counter: 79 },
        { Name: '云南省', Amount: 128, Counter: 77 }
    ]
});

/* ---------------------------- 适应症维度 ---------------------------- */

// 目标适应症用药组合（树图）：[ { DiseaseName, DrugName, DrugCount } ]
const diseaseUnion = (keyword) => {
    const rows = [
        { DiseaseName: '甲状腺结节', DrugName: '左甲状腺素钠片', DrugCount: 320 },
        { DiseaseName: '甲状腺结节', DrugName: '夏枯草胶囊', DrugCount: 268 },
        { DiseaseName: '甲状腺结节', DrugName: '小金丸', DrugCount: 214 },
        { DiseaseName: '甲状腺结节', DrugName: '内消瘰疬丸', DrugCount: 176 },
        { DiseaseName: '甲状腺功能亢进', DrugName: '甲巯咪唑片', DrugCount: 286 },
        { DiseaseName: '甲状腺功能亢进', DrugName: '丙硫氧嘧啶片', DrugCount: 232 },
        { DiseaseName: '甲状腺功能亢进', DrugName: '普萘洛尔片', DrugCount: 188 },
        { DiseaseName: '甲状腺功能亢进', DrugName: '夏枯草胶囊', DrugCount: 152 },
        { DiseaseName: '甲状腺功能减退', DrugName: '左甲状腺素钠片', DrugCount: 298 },
        { DiseaseName: '甲状腺功能减退', DrugName: '甲状腺片', DrugCount: 204 },
        { DiseaseName: '甲状腺功能减退', DrugName: '金匮肾气丸', DrugCount: 148 },
        { DiseaseName: '甲状腺炎', DrugName: '泼尼松片', DrugCount: 196 },
        { DiseaseName: '甲状腺炎', DrugName: '布洛芬缓释胶囊', DrugCount: 164 },
        { DiseaseName: '甲状腺炎', DrugName: '左甲状腺素钠片', DrugCount: 128 }
    ];
    return { code: '200', data: filterRows(rows, keyword, ['DiseaseName', 'DrugName']) };
};

// 目标适应症联合用药（和弦图）：{ Nodes: [{ name, value }], Links: [{ source, target, weight }] }
const diseaseDrug = () => {
    const names = ['左甲状腺素钠片', '甲巯咪唑片', '夏枯草胶囊', '普萘洛尔片', '丙硫氧嘧啶片', '小金丸'];
    const values = [420, 360, 300, 240, 200, 160];
    const nodes = names.map((name, index) => ({ name, value: values[index] }));
    // 联合出现的次数（source / target 为 Nodes 数组下标，也可以用名称）
    const pairs = [
        [0, 1, 86], [0, 2, 74], [0, 3, 62], [0, 4, 48], [0, 5, 36],
        [1, 2, 54], [1, 3, 46], [1, 4, 40], [1, 5, 28],
        [2, 3, 34], [2, 4, 26], [2, 5, 30],
        [3, 4, 22], [3, 5, 18],
        [4, 5, 16]
    ];
    return {
        code: '200',
        data: {
            Nodes: nodes,
            Links: pairs.map(p => ({ source: p[0], target: p[1], weight: p[2] }))
        }
    };
};

// 目标适应症不同年龄人群分布（散点图）：[ { Sex: '10'男 / '20'女, Age, Counter } ]
const diseaseAge = () => {
    const ages = [6, 12, 18, 24, 32, 40, 48, 56, 64, 72, 80];
    const rows = [];
    ages.forEach((age, index) => {
        rows.push({ Sex: '10', Age: age, Counter: 120 + index * 26 + (index % 3) * 18 });
        rows.push({ Sex: '20', Age: age, Counter: 140 + index * 22 + (index % 2) * 26 });
    });
    return { code: '200', data: rows };
};

// 目标适应症对应科室分布（饼图）：[ { SectionName, Counter } ]
const diseaseSection = () => ({
    code: '200',
    data: [
        { SectionName: '内分泌科', Counter: 320 },
        { SectionName: '普通内科', Counter: 265 },
        { SectionName: '甲状腺外科', Counter: 208 },
        { SectionName: '核医学科', Counter: 156 },
        { SectionName: '中医科', Counter: 132 },
        { SectionName: '超声科', Counter: 98 },
        { SectionName: '全科医学科', Counter: 76 }
    ]
});

/* ---------------------------- 药品维度 ---------------------------- */

// 药品品牌覆盖城市（柱状图）：[ { Name, Counter } ]
const drugCities = () => ({
    code: '200',
    data: [
        { Name: '北京市', Counter: 320 },
        { Name: '上海市', Counter: 298 },
        { Name: '广州市', Counter: 276 },
        { Name: '深圳市', Counter: 254 },
        { Name: '成都市', Counter: 232 },
        { Name: '杭州市', Counter: 214 },
        { Name: '武汉市', Counter: 196 },
        { Name: '南京市', Counter: 182 },
        { Name: '西安市', Counter: 168 },
        { Name: '沈阳市', Counter: 152 },
        { Name: '长沙市', Counter: 138 },
        { Name: '郑州市', Counter: 126 }
    ]
});

// 药品品牌覆盖医院（堆叠柱状图）：[ { Drug, Grade（一级~四级）, Counter } ]
const drugHospital = () => {
    const drugs = ['人参药酒', '复方丹参滴丸', '阿莫西林胶囊', '布洛芬缓释胶囊'];
    const grades = ['一级', '二级', '三级', '四级'];
    const rows = [];
    drugs.forEach((drug, di) => {
        grades.forEach((grade, gi) => {
            rows.push({
                Drug: drug,
                Grade: grade,
                Counter: 40 + (3 - gi) * 26 + (3 - di) * 14
            });
        });
    });
    return { code: '200', data: rows };
};

// 目标药品对应适应症（旭日图）：[ { Drug, Disease, Counter } ]
const drugDiseases = (keyword) => {
    const rows = [
        { Drug: '人参药酒', Disease: '气血两虚证', Counter: 186 },
        { Drug: '人参药酒', Disease: '脾胃虚弱证', Counter: 152 },
        { Drug: '人参药酒', Disease: '心悸失眠', Counter: 118 },
        { Drug: '复方丹参滴丸', Disease: '冠心病心绞痛', Counter: 264 },
        { Drug: '复方丹参滴丸', Disease: '高脂血症', Counter: 176 },
        { Drug: '复方丹参滴丸', Disease: '胸痹心痛', Counter: 132 },
        { Drug: '阿莫西林胶囊', Disease: '上呼吸道感染', Counter: 286 },
        { Drug: '阿莫西林胶囊', Disease: '急性支气管炎', Counter: 198 },
        { Drug: '阿莫西林胶囊', Disease: '尿路感染', Counter: 146 },
        { Drug: '布洛芬缓释胶囊', Disease: '骨关节炎', Counter: 216 },
        { Drug: '布洛芬缓释胶囊', Disease: '偏头痛', Counter: 168 },
        { Drug: '布洛芬缓释胶囊', Disease: '牙周炎', Counter: 124 }
    ];
    return { code: '200', data: filterRows(rows, keyword, ['Drug', 'Disease']) };
};

// 目标药品科室分布（矩形树图）：[ { Drug, Section, Counter } ]
const drugSection = (keyword) => {
    const rows = [
        { Drug: '人参药酒', Section: '中医科', Counter: 186 },
        { Drug: '人参药酒', Section: '普通内科', Counter: 132 },
        { Drug: '人参药酒', Section: '老年病科', Counter: 96 },
        { Drug: '复方丹参滴丸', Section: '心血管内科', Counter: 264 },
        { Drug: '复方丹参滴丸', Section: '中医科', Counter: 158 },
        { Drug: '复方丹参滴丸', Section: '急诊科', Counter: 104 },
        { Drug: '阿莫西林胶囊', Section: '呼吸内科', Counter: 286 },
        { Drug: '阿莫西林胶囊', Section: '泌尿外科', Counter: 168 },
        { Drug: '阿莫西林胶囊', Section: '儿科', Counter: 122 },
        { Drug: '布洛芬缓释胶囊', Section: '骨科', Counter: 216 },
        { Drug: '布洛芬缓释胶囊', Section: '神经内科', Counter: 148 },
        { Drug: '布洛芬缓释胶囊', Section: '口腔科', Counter: 112 }
    ];
    return { code: '200', data: filterRows(rows, keyword, ['Drug', 'Section']) };
};

/* ---------------------------- 工具函数 ---------------------------- */

/**
 * 关键字过滤：命中则过滤，没有命中就返回全量（避免页面直接空白）
 */
function filterRows(rows, keyword, fields) {
    if (!keyword) return rows;
    const kw = String(keyword).trim();
    if (!kw) return rows;
    const hit = rows.filter(row => fields.some(field => String(row[field]).indexOf(kw) > -1));
    return hit.length > 0 ? hit : rows;
}

export default {
    '/home/overview': overview,
    '/home/citylevel': cityLevel,
    '/home/age': age,
    '/home/top10': top10,
    '/home/province': province,
    '/disease/union': diseaseUnion,
    '/disease/drug': diseaseDrug,
    '/disease/age': diseaseAge,
    '/disease/section': diseaseSection,
    '/drug/cities': drugCities,
    '/drug/hospital': drugHospital,
    '/drug/diseases': drugDiseases,
    '/drug/section': drugSection
};
