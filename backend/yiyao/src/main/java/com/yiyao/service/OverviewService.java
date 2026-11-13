package com.yiyao.service;

import com.yiyao.kylin.KylinUtil;
import com.yiyao.mapper.StatsMapper;
import com.yiyao.output.OverviewOutput;
import org.springframework.beans.factory.BeanFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 首页概览指标。
 *
 * 取数分两路：
 * 1. 处方总数 / 销售总额 / 覆盖医院 —— 走 Kylin 立方体，只用事实表，不 JOIN 维表，
 * 因此不依赖模型里是否挂了 lookup 表。
 * 2. 收录药品 / 收录适应症 / 覆盖城市 —— 走 MySQL 维表的 COUNT，数据量小、毫秒级。
 *
 * 两段各自 try/catch：任意一段失败只影响对应的几张卡片，不会让整个接口 500。
 */
@Service
public class OverviewService {

	@Autowired
	private BeanFactory beanFactory;

	@Autowired
	private StatsMapper statsMapper;

	/**
	 * 首页 6 个指标卡片
	 *
	 * @return 指标列表
	 */
	public List<OverviewOutput> overview() {

		long rowsCnt = 0L;
		double totalAmount = 0D;
		long hospCnt = 0L;

		// ① 事实表指标：处方总数 / 销售总额 / 覆盖医院
		//    这条 SQL 只查事实表、不 JOIN 维表，所以 Kylin 和 MySQL 两种引擎都能跑；
		//    实际由 query.engine 决定落到哪个库，SQL 本身不需要区分。
		try {
			String sql = "SELECT" +
					" COUNT(1) AS \"rowsCnt\"," +
					" SUM(AMOUNT) AS \"totalAmount\"," +
					" COUNT(DISTINCT HOSP_ID) AS \"hospCnt\"" +
					" FROM BIGDATA.PRESCRIPTION_DISEASES";
			List<Map<String, Object>> res = beanFactory.getBean(KylinUtil.class).QueryForList(sql);
			if (res != null && !res.isEmpty()) {
				Map<String, Object> row = res.get(0);
				rowsCnt = toLong(get(row, "rowsCnt"));
				totalAmount = toDouble(get(row, "totalAmount"));
				hospCnt = toLong(get(row, "hospCnt"));
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		// ② MySQL 维表：字典规模
		long drugCnt = 0L;
		long diseaseCnt = 0L;
		long cityCnt = 0L;
		try {
			Map<String, Object> row = statsMapper.countDictionary();
			if (row != null) {
				drugCnt = toLong(get(row, "DRUG_CNT"));
				diseaseCnt = toLong(get(row, "DISEASE_CNT"));
				cityCnt = toLong(get(row, "CITY_CNT"));
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		List<OverviewOutput> list = new ArrayList<>();
		list.add(new OverviewOutput("处方总数", rowsCnt, "条"));
		list.add(new OverviewOutput("销售总额", round2(totalAmount), "元"));
		list.add(new OverviewOutput("覆盖医院", hospCnt, "家"));
		list.add(new OverviewOutput("收录药品", drugCnt, "种"));
		list.add(new OverviewOutput("收录适应症", diseaseCnt, "种"));
		list.add(new OverviewOutput("覆盖城市", cityCnt, "个"));
		return list;
	}

	/**
	 * 大小写不敏感地取 Map 里的值。
	 * Kylin JDBC 与 MySQL JDBC 对列标签的大小写处理不一致，统一在这里兜住。
	 */
	private Object get(Map<String, Object> map, String key) {
		if (map == null) return null;
		if (map.containsKey(key)) return map.get(key);
		for (Map.Entry<String, Object> e : map.entrySet()) {
			if (e.getKey() != null && e.getKey().equalsIgnoreCase(key)) return e.getValue();
		}
		return null;
	}

	private long toLong(Object v) {
		if (v == null) return 0L;
		if (v instanceof Number) return ((Number) v).longValue();
		try {
			return Long.parseLong(String.valueOf(v).trim());
		} catch (NumberFormatException e) {
			return 0L;
		}
	}

	private double toDouble(Object v) {
		if (v == null) return 0D;
		if (v instanceof Number) return ((Number) v).doubleValue();
		try {
			return Double.parseDouble(String.valueOf(v).trim());
		} catch (NumberFormatException e) {
			return 0D;
		}
	}

	/**
	 * 保留两位小数。
	 * 这里必须返回 BigDecimal 而不是 double：
	 * double 序列化成 JSON 时，26239620.54 会被 Jackson 输出为科学计数法 2.623962054E7，
	 * 首页卡片就会显示成一行看不懂的数字。BigDecimal 按原样输出。
	 */
	private BigDecimal round2(double v) {
		return BigDecimal.valueOf(v).setScale(2, RoundingMode.HALF_UP);
	}
}
