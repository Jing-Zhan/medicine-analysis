package com.yiyao.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Map;

/**
 * 用药结构对比查询。
 *
 * 数据来源是 agg_section_drug 与 agg_cat_drug 两张预聚合表，
 * 聚合粒度是「科室或疾病大类 × 药品编码 × 处方数」。
 * 查询时与药品维表关联，把处方数按剂型、基本药物、抗菌药物三个属性拆开，
 * 用来回答「哪个科室或哪类疾病的用药结构与其他明显不同」。
 *
 * 前置条件：agg_structure.sql 已执行。
 */
@Mapper
public interface StructureMapper {

	/** 抗菌药物通用名关键词，与 DrugService 中的口径保持一致 */
	String ANTI = "'霉素|西林|头孢|沙星|环素|培南|硝唑|磺胺|呋喃'";

	/**
	 * 按科室汇总用药结构，返回 name / records / inj / ess / anti。
	 */
	@Select("SELECT x.section_name AS name, SUM(x.cnt) AS records, "
			+ "SUM(CASE WHEN g.form_name1 LIKE '%注射%' THEN x.cnt ELSE 0 END) AS inj, "
			+ "SUM(CASE WHEN TRIM(g.is_essential_drug) IN ('是','1','Y','YES','y') THEN x.cnt ELSE 0 END) AS ess, "
			+ "SUM(CASE WHEN g.drug_generic_name REGEXP " + ANTI + " THEN x.cnt ELSE 0 END) AS anti "
			+ "FROM agg_section_drug x JOIN t_view_drug g ON x.drug_code = g.drug "
			+ "GROUP BY x.section_name ORDER BY records DESC LIMIT #{limit}")
	List<Map<String, Object>> sectionStructure(@Param("limit") int limit);

	/**
	 * 按疾病大类汇总用药结构，返回 name / records / inj / ess / anti。
	 */
	@Select("SELECT x.cat_name AS name, SUM(x.cnt) AS records, "
			+ "SUM(CASE WHEN g.form_name1 LIKE '%注射%' THEN x.cnt ELSE 0 END) AS inj, "
			+ "SUM(CASE WHEN TRIM(g.is_essential_drug) IN ('是','1','Y','YES','y') THEN x.cnt ELSE 0 END) AS ess, "
			+ "SUM(CASE WHEN g.drug_generic_name REGEXP " + ANTI + " THEN x.cnt ELSE 0 END) AS anti "
			+ "FROM agg_cat_drug x JOIN t_view_drug g ON x.drug_code = g.drug "
			+ "GROUP BY x.cat_name ORDER BY records DESC LIMIT #{limit}")
	List<Map<String, Object>> categoryStructure(@Param("limit") int limit);
}
