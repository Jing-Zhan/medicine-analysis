package com.yiyao.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.yiyao.entity.DrugEntity;
import com.yiyao.kylin.KylinUtil;
import com.yiyao.mapper.DrugMapper;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.BeanFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 药品业务实现接口
 */
@Service
public class DrugService {

	/**
	 * bean容器
	 */
	@Autowired
	private BeanFactory beanFactory;

	/**
	 * 数据库查询接口
	 */
	@Autowired
	private DrugMapper drugMapper;

	/**
	 * 药品对应城市信息
	 *
	 * @param keyword 关键字
	 * @return 药品对应城市信息
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> queryCities(String keyword) throws Exception {

		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DrugEntity> list = drugQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DrugEntity::getDrug).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DRUG.DRUG in('" + String.join("','", diseaseCodes) + "')";
			}
		}

		//查询立方体语句
		String sql = "SELECT " +
				" HOSP_AREA.CITY_NAME as \"name\",count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' and HOSP_AREA.CITY_NAME!='' group by HOSP_AREA.CITY_NAME";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);
	}

	/**
	 * 根据药品关键字查询医院信息
	 *
	 * @param keyword 药品关键字
	 * @return 医院信息
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> queryHospitals(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DrugEntity> list = drugQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DrugEntity::getDrug).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DRUG.DRUG in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" DRUG.DRUG_GENERIC_NAME as \"drug\",HOSPITAL.HOSP_GRADE_NAME as \"grade\",count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" LEFT JOIN BIGDATA.HOSPITAL as HOSPITAL" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSPITAL.HOSP_ID" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' group by DRUG.DRUG_GENERIC_NAME,HOSPITAL.HOSP_GRADE_NAME limit 20";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);
	}

	/**
	 * 根据药品关键字查询目标适应症
	 *
	 * @param keyword 药品关键字
	 * @return 目标适应症
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> queryDiseases(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DrugEntity> list = drugQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DrugEntity::getDrug).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DRUG.DRUG in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" DRUG.DRUG_GENERIC_NAME as \"drug\",DISEASE.DISEASE_TYPE_NAME13 as \"disease\",count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" LEFT JOIN BIGDATA.DISEASE as DISEASE" +
				" ON PRESCRIPTION_DISEASES.M_DIAGNOSTIC = DISEASE.DISEASE_TYPE13" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' group by DRUG.DRUG_GENERIC_NAME,DISEASE.DISEASE_TYPE_NAME13 order by count(0) desc limit 20";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);
	}

	/**
	 * 根据目标关键字查询科室信息
	 *
	 * @param keyword 关键字
	 * @return 科室信息
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> querySections(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DrugEntity> list = drugQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DrugEntity::getDrug).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DRUG.DRUG in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" DRUG.DRUG_GENERIC_NAME as \"drug\",SECTION.SECTION_NAME1 as \"section\",count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" LEFT JOIN BIGDATA.SECTION as SECTION" +
				" ON PRESCRIPTION_DISEASES.M_SECTION = SECTION.SECTION2" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' group by DRUG.DRUG_GENERIC_NAME,SECTION.SECTION_NAME1 order by count(0) desc limit 20";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);
	}

	/**
	 * 查询药品品牌前10
	 *
	 * @return 药品品牌前10
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> top10amount() throws Exception {
		//查询立方体语句
		String sql = "SELECT " +
				" DRUG.DRUG_GENERIC_NAME as \"name\" " +
				" ,sum(PRESCRIPTION_DISEASES.PRICE) as \"price\" " +
				" ,sum(PRESCRIPTION_DISEASES.AMOUNT) as \"amount\", " +
				" count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES " +
				" LEFT JOIN BIGDATA.DRUG as DRUG " +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG " +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA " +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID " +
				" WHERE 1=1  " +
				" group by DRUG.DRUG_GENERIC_NAME " +
				" order by sum(PRESCRIPTION_DISEASES.AMOUNT) desc limit 10";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);
	}

	/**
	 * 查询药品各省份使用情况
	 *
	 * @return 品各省份使用情况
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> provinceTotal() throws Exception {
		//查询立方体语句
		String sql = "SELECT " +
				" HOSP_AREA.PROVINCE_NAME as \"name\" " +
				" ,round(sum(PRESCRIPTION_DISEASES.PRICE),2) as \"price\" " +
				" ,round(sum(PRESCRIPTION_DISEASES.AMOUNT),2) as \"amount\", " +
				" count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES " +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA " +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID " +
				" WHERE 1=1  " +
				" group by HOSP_AREA.PROVINCE_NAME ";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);
	}

	private List<DrugEntity> drugQueryByKeyword(String keyword) {
		QueryWrapper<DrugEntity> query = new QueryWrapper<>();
		if (StringUtils.isNotBlank(keyword)) query.like("package_chinese_name", keyword);
		return drugMapper.selectList(query);
	}
}
