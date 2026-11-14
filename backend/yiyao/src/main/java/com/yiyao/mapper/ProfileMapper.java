package com.yiyao.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Map;

/**
 * 适应症画像与药品画像的取数接口。
 *
 * 数据来源是预计算表（见 deploy/sql/agg_profile.sql）：
 *   agg_disease_total  每个适应症的处方数、金额
 *   agg_drug_total     每个药品的处方数、金额
 *   agg_disease_drug   适应症×药品的计数，并冗余两个分母与全局总数
 *
 * 因为两个分母已经冗余在同一行里，取关联榜只需要一次单表查询，不用连表。
 * 结构分布走明细表，按疾病编码或药品编码过滤后行数有限，
 * 依赖 idx_diag1 与 idx_drug_code 两个索引。
 *
 * 注意：count 是 MySQL 的函数名，这里统一用 cnt 作别名，避免解析歧义。
 */
@Repository
@Mapper
public interface ProfileMapper {

	// ---------------------------------------------------------------- 目标对象

	@Select("SELECT disease_code AS code, disease_name AS name, cnt AS records, amount AS amount "
			+ "FROM agg_disease_total WHERE disease_code = #{key} LIMIT 1")
	Map<String, Object> diseaseByCode(@Param("key") String key);

	@Select("SELECT disease_code AS code, disease_name AS name, cnt AS records, amount AS amount "
			+ "FROM agg_disease_total WHERE disease_name LIKE CONCAT('%', #{key}, '%') "
			+ "ORDER BY cnt DESC LIMIT 1")
	Map<String, Object> diseaseByKeyword(@Param("key") String key);

	@Select("SELECT drug_code AS code, drug_name AS name, cnt AS records, amount AS amount "
			+ "FROM agg_drug_total WHERE drug_code = #{key} LIMIT 1")
	Map<String, Object> drugByCode(@Param("key") String key);

	@Select("SELECT drug_code AS code, drug_name AS name, cnt AS records, amount AS amount "
			+ "FROM agg_drug_total WHERE drug_name LIKE CONCAT('%', #{key}, '%') "
			+ "ORDER BY cnt DESC LIMIT 1")
	Map<String, Object> drugByKeyword(@Param("key") String key);

	/**
	 * 全库处方数，作为支持度与占比的分母
	 */
	@Select("SELECT COALESCE(SUM(cnt), 0) FROM agg_disease_total")
	long grandTotal();

	/**
	 * 不传参数时的默认对象：处方量最大的适应症
	 */
	@Select("SELECT disease_code AS code, disease_name AS name, cnt AS records, amount AS amount "
			+ "FROM agg_disease_total ORDER BY cnt DESC LIMIT 1")
	Map<String, Object> topDisease();

	/**
	 * 不传参数时的默认对象：处方量最大的药品
	 */
	@Select("SELECT drug_code AS code, drug_name AS name, cnt AS records, amount AS amount "
			+ "FROM agg_drug_total ORDER BY cnt DESC LIMIT 1")
	Map<String, Object> topDrug();

	// ---------------------------------------------------------------- 关联榜

	/**
	 * 某适应症下的全部药品组合。置信度分母为 fix_total，提升度分母为 var_total。
	 */
	@Select("SELECT drug_code AS code, drug_name AS name, cnt AS cnt, "
			+ "disease_total AS fix_total, drug_total AS var_total "
			+ "FROM agg_disease_drug WHERE disease_code = #{code} AND cnt >= #{minCount}")
	List<Map<String, Object>> drugsOfDisease(@Param("code") String code,
											 @Param("minCount") int minCount);

	/**
	 * 某药品下的全部适应症组合。置信度分母为 fix_total，提升度分母为 var_total。
	 */
	@Select("SELECT disease_code AS code, disease_name AS name, cnt AS cnt, "
			+ "drug_total AS fix_total, disease_total AS var_total "
			+ "FROM agg_disease_drug WHERE drug_code = #{code} AND cnt >= #{minCount}")
	List<Map<String, Object>> diseasesOfDrug(@Param("code") String code,
											 @Param("minCount") int minCount);

	// ---------------------------------------------------------------- 结构分布

	@Select("SELECT m_age AS k, COUNT(*) AS c FROM prescription_diseases "
			+ "WHERE m_diagnostic1 = #{code} GROUP BY m_age")
	List<Map<String, Object>> ageOfDisease(@Param("code") String code);

	@Select("SELECT m_age AS k, COUNT(*) AS c FROM prescription_diseases "
			+ "WHERE drug_code = #{code} GROUP BY m_age")
	List<Map<String, Object>> ageOfDrug(@Param("code") String code);

	@Select("SELECT COALESCE(NULLIF(s.section_name1, ''), '未标注') AS name, COUNT(*) AS cnt "
			+ "FROM prescription_diseases p JOIN t_view_section s ON p.m_section = s.section2 "
			+ "WHERE p.m_diagnostic1 = #{code} GROUP BY 1 ORDER BY cnt DESC LIMIT 5")
	List<Map<String, Object>> sectionsOfDisease(@Param("code") String code);

	@Select("SELECT COALESCE(NULLIF(s.section_name1, ''), '未标注') AS name, COUNT(*) AS cnt "
			+ "FROM prescription_diseases p JOIN t_view_section s ON p.m_section = s.section2 "
			+ "WHERE p.drug_code = #{code} GROUP BY 1 ORDER BY cnt DESC LIMIT 5")
	List<Map<String, Object>> sectionsOfDrug(@Param("code") String code);

	@Select("SELECT COALESCE(NULLIF(a.province_name, ''), '未标注') AS name, COUNT(*) AS cnt "
			+ "FROM prescription_diseases p JOIN t_view_areas a ON p.hosp_id = a.hosp_id "
			+ "WHERE p.m_diagnostic1 = #{code} GROUP BY 1 ORDER BY cnt DESC LIMIT 5")
	List<Map<String, Object>> provincesOfDisease(@Param("code") String code);

	@Select("SELECT COALESCE(NULLIF(a.city_name, ''), '未标注') AS name, COUNT(*) AS cnt "
			+ "FROM prescription_diseases p JOIN t_view_areas a ON p.hosp_id = a.hosp_id "
			+ "WHERE p.drug_code = #{code} GROUP BY 1 ORDER BY cnt DESC LIMIT 5")
	List<Map<String, Object>> citiesOfDrug(@Param("code") String code);

	// ---------------------------------------------------------------- 属性标签

	@Select("SELECT is_essential_drug AS v, COUNT(*) AS c FROM t_view_drug WHERE drug = #{code} GROUP BY 1 ORDER BY c DESC")
	List<Map<String, Object>> essentialOfDrug(@Param("code") String code);

	@Select("SELECT is_otc AS v, COUNT(*) AS c FROM t_view_drug WHERE drug = #{code} GROUP BY 1 ORDER BY c DESC")
	List<Map<String, Object>> otcOfDrug(@Param("code") String code);

	@Select("SELECT is_special_drug AS v, COUNT(*) AS c FROM t_view_drug WHERE drug = #{code} GROUP BY 1 ORDER BY c DESC")
	List<Map<String, Object>> specialOfDrug(@Param("code") String code);

	@Select("SELECT risk_pregnancy_grade AS v, COUNT(*) AS c FROM t_view_drug WHERE drug = #{code} GROUP BY 1 ORDER BY c DESC")
	List<Map<String, Object>> pregnancyOfDrug(@Param("code") String code);

	/**
	 * 该适应症的处方里，基本药物与非基本药物的处方数分布
	 */
	@Select("SELECT COALESCE(NULLIF(g.is_essential_drug, ''), '未记录') AS v, COUNT(*) AS c "
			+ "FROM prescription_diseases p JOIN t_view_drug g ON p.drug_code = g.drug "
			+ "WHERE p.m_diagnostic1 = #{code} GROUP BY 1 ORDER BY c DESC LIMIT 2")
	List<Map<String, Object>> essentialOfDisease(@Param("code") String code);

	@Select("SELECT COALESCE(NULLIF(g.is_otc, ''), '未记录') AS v, COUNT(*) AS c "
			+ "FROM prescription_diseases p JOIN t_view_drug g ON p.drug_code = g.drug "
			+ "WHERE p.m_diagnostic1 = #{code} GROUP BY 1 ORDER BY c DESC LIMIT 2")
	List<Map<String, Object>> otcOfDisease(@Param("code") String code);

	/**
	 * 疾病三级分类：细目所属的大类与中类名称，用于画像里显示层级归属
	 */
	@Select("SELECT COALESCE(NULLIF(disease_type_name11, ''), '未分类') AS cat, "
			+ "COALESCE(NULLIF(disease_type_name12, ''), '未分类') AS sub "
			+ "FROM t_view_disease WHERE disease_type13 = #{code} LIMIT 1")
	Map<String, Object> diseaseHierarchy(@Param("code") String code);

	// ---------------------------------------------------------------- 构成分析

	/**
	 * 疾病分层构成：level 取 11 大类、12 中类、13 细目。
	 * 走 agg_disease_total 四万行，再关联四万行的疾病维表，避免直接连一百万行事实表。
	 */
	@Select("SELECT COALESCE(NULLIF(d.disease_type_name11, ''), '未分类') AS name, SUM(a.cnt) AS cnt "
			+ "FROM agg_disease_total a JOIN t_view_disease d ON a.disease_code = d.disease_type13 "
			+ "GROUP BY 1 ORDER BY cnt DESC LIMIT #{limit}")
	List<Map<String, Object>> categoryLevel11(@Param("limit") int limit);

	@Select("SELECT COALESCE(NULLIF(d.disease_type_name12, ''), '未分类') AS name, SUM(a.cnt) AS cnt "
			+ "FROM agg_disease_total a JOIN t_view_disease d ON a.disease_code = d.disease_type13 "
			+ "GROUP BY 1 ORDER BY cnt DESC LIMIT #{limit}")
	List<Map<String, Object>> categoryLevel12(@Param("limit") int limit);

	@Select("SELECT COALESCE(NULLIF(d.disease_type_name13, ''), '未分类') AS name, SUM(a.cnt) AS cnt "
			+ "FROM agg_disease_total a JOIN t_view_disease d ON a.disease_code = d.disease_type13 "
			+ "GROUP BY 1 ORDER BY cnt DESC LIMIT #{limit}")
	List<Map<String, Object>> categoryLevel13(@Param("limit") int limit);

	/**
	 * 药品属性构成：col 必须是白名单内的列名，由 Service 校验后再传入。
	 * 走 agg_drug_total 二十万行，再关联药品维表。
	 */
	@Select("SELECT COALESCE(NULLIF(g.${col}, ''), '未标注') AS name, SUM(a.cnt) AS cnt "
			+ "FROM agg_drug_total a JOIN t_view_drug g ON a.drug_code = g.drug "
			+ "GROUP BY 1 ORDER BY cnt DESC LIMIT #{limit}")
	List<Map<String, Object>> drugAttribute(@Param("col") String col, @Param("limit") int limit);

	// ---------------------------------------------------------------- 费用负担与市场结构

	/**
	 * 疾病费用负担：按疾病层级汇总处方数、金额与均次费用。
	 * 走 agg_disease_total 四万行，不碰一百万行事实表。
	 */
	@Select("SELECT COALESCE(NULLIF(d.disease_type_name11, ''), '未分类') AS name, SUM(a.cnt) AS records, "
			+ "ROUND(SUM(a.amount), 2) AS amount "
			+ "FROM agg_disease_total a JOIN t_view_disease d ON a.disease_code = d.disease_type13 "
			+ "GROUP BY 1 ORDER BY amount DESC LIMIT #{limit}")
	List<Map<String, Object>> burdenLevel11(@Param("limit") int limit);

	@Select("SELECT COALESCE(NULLIF(d.disease_type_name12, ''), '未分类') AS name, SUM(a.cnt) AS records, "
			+ "ROUND(SUM(a.amount), 2) AS amount "
			+ "FROM agg_disease_total a JOIN t_view_disease d ON a.disease_code = d.disease_type13 "
			+ "GROUP BY 1 ORDER BY amount DESC LIMIT #{limit}")
	List<Map<String, Object>> burdenLevel12(@Param("limit") int limit);

	@Select("SELECT COALESCE(NULLIF(d.disease_type_name13, ''), '未分类') AS name, SUM(a.cnt) AS records, "
			+ "ROUND(SUM(a.amount), 2) AS amount "
			+ "FROM agg_disease_total a JOIN t_view_disease d ON a.disease_code = d.disease_type13 "
			+ "GROUP BY 1 ORDER BY amount DESC LIMIT #{limit}")
	List<Map<String, Object>> burdenLevel13(@Param("limit") int limit);

	/**
	 * 全部厂商的销售金额，用于计算份额、CR10 与 HHI。
	 *
	 * company_name 列在导入时有错位，少量记录存的是剂型值，例如「口服」「注射」，
	 * 不处理会让这些值排到厂商榜前两位。这里要求名称包含企业特征词才计入，
	 * 过滤后仍是七千多家，一次取回在 Java 里算，避免在 SQL 里做多次聚合。
	 */
	@Select("SELECT COALESCE(NULLIF(g.company_name, ''), '未标注') AS name, "
			+ "ROUND(SUM(a.amount), 2) AS amount "
			+ "FROM agg_drug_total a JOIN t_view_drug g ON a.drug_code = g.drug "
			+ "WHERE g.company_name REGEXP '公司|厂|集团|药业|制药|研究院|生物|医药|科技' "
			+ "GROUP BY 1 ORDER BY amount DESC")
	List<Map<String, Object>> vendorAmounts();

	/**
	 * 合理用药指标：按处方数加权的各类占比，一行返回全部分子与分母。
	 */
	@Select("SELECT "
			+ "SUM(CASE WHEN g.form_name1 LIKE '%注射%' THEN a.cnt ELSE 0 END) AS inj, "
			+ "SUM(CASE WHEN g.is_essential_drug IN ('是','1','Y','YES','y') THEN a.cnt ELSE 0 END) AS ess, "
			+ "SUM(CASE WHEN g.is_otc IN ('是','1','Y','YES','y') THEN a.cnt ELSE 0 END) AS otc, "
			+ "SUM(CASE WHEN g.is_special_drug IN ('是','1','Y','YES','y') THEN a.cnt ELSE 0 END) AS sp, "
			+ "SUM(CASE WHEN g.drug_generic_name REGEXP '霉素|西林|头孢|沙星|环素|培南|硝唑|磺胺|呋喃' "
			+ "THEN a.cnt ELSE 0 END) AS anti, SUM(a.cnt) AS total "
			+ "FROM agg_drug_total a JOIN t_view_drug g ON a.drug_code = g.drug")
	Map<String, Object> drugIndicators();
}
