package com.yiyao.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.springframework.stereotype.Repository;

import java.util.Map;

/**
 * 首页概览的补充统计。
 *
 * 立方体里只有 8 个维度和 4 个度量，算不出「收录药品 / 收录适应症 / 覆盖城市」这类
 * 字典总量，所以走 MySQL 的维表。三张表都很小（药品 23 万、疾病 4.2 万、区域 1777），
 * 三个子查询一次返回，耗时在毫秒级，不影响首页加载。
 */
@Repository
@Mapper
public interface StatsMapper {

	/**
	 * 字典规模统计。
	 *
	 * @return DRUG_CNT / DISEASE_CNT / CITY_CNT
	 */
	@Select("SELECT" +
			" (SELECT COUNT(*) FROM t_view_drug) AS DRUG_CNT," +
			" (SELECT COUNT(*) FROM t_view_disease) AS DISEASE_CNT," +
			" (SELECT COUNT(DISTINCT city) FROM t_view_areas) AS CITY_CNT")
	Map<String, Object> countDictionary();
}
