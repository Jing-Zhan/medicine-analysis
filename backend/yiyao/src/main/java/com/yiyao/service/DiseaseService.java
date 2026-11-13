package com.yiyao.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.yiyao.entity.DiseaseEntity;
import com.yiyao.kylin.KylinUtil;
import com.yiyao.mapper.DiseaseMapper;
import com.yiyao.output.*;
import com.yiyao.util.MapUtil;
import com.yiyao.util.MathsUtil;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.BeanFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 疾病接口
 */
@Service
public class DiseaseService {

	/**
	 * 目标适应症数据库接口
	 */
	@Autowired
	private DiseaseMapper diseaseMapper;

	/**
	 * bean容器
	 */
	@Autowired
	private BeanFactory beanFactory;

	/**
	 * 从数据库中查询目标适应症
	 *
	 * @param keyword 关键字
	 * @return 目标适应症
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> queryDiseaseFromDb(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DiseaseEntity> list = diseaseQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DiseaseEntity::getDiseaseType3).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DISEASE.DISEASE_TYPE13 in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" DISEASE.DISEASE_TYPE_NAME13 as \"diseaseName\",DRUG.DRUG_GENERIC_NAME as \"drugName\",count(0) as \"drugCount\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DISEASE as DISEASE" +
				" ON PRESCRIPTION_DISEASES.M_DIAGNOSTIC = DISEASE.DISEASE_TYPE13" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' " +
				" group by DISEASE.DISEASE_TYPE_NAME13,DRUG_GENERIC_NAME order by count(0) desc limit 20";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);

	}

	/**
	 * 从数据库中查询目标适应症联合用药
	 *
	 * @param keyword 关键字
	 * @return 目标适应症联合用药
	 * @throws Exception kylin查询异常
	 */
	public DiseaseDrugUnionOutput queryDiseaseDrugFromDb(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DiseaseEntity> list = diseaseQueryByKeyword(keyword);
			if (list.isEmpty()) return new DiseaseDrugUnionOutput();
			List<String> diseaseCodes = list.stream().map(DiseaseEntity::getDiseaseType3).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DISEASE.DISEASE_TYPE13 in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" DISEASE.DISEASE_TYPE_NAME13 as \"diseaseName\",DRUG.DRUG_GENERIC_NAME as \"drugName\",count(0) as \"drugCount\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DISEASE as DISEASE" +
				" ON PRESCRIPTION_DISEASES.M_DIAGNOSTIC = DISEASE.DISEASE_TYPE13" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' " +
				" group by DISEASE.DISEASE_TYPE_NAME13,DRUG_GENERIC_NAME order by count(0) desc limit 20";
		//执行kylin查询
		List<Map<String, Object>> searchResult = beanFactory.getBean(KylinUtil.class).QueryForList(sql);

		//按照接口格式重新排列数据
		List<DiseaseDrugNode> nodes = new ArrayList<>();
		List<Object> linkList = new ArrayList<>();
		searchResult.forEach(m -> {
			if (!nodes.stream().anyMatch(a -> a.getName().equals(m.get("diseaseName")))) {
				DiseaseDrugNode detail = new DiseaseDrugNode();
				detail.setName(String.valueOf(m.get("diseaseName")));
				nodes.add(detail);
			}
			if (!nodes.stream().anyMatch(a -> a.getName().equals(m.get("drugName")))) {
				DiseaseDrugNode detail = new DiseaseDrugNode();
				detail.setName(String.valueOf(m.get("drugName")));
				nodes.add(detail);
			}
			DiseaseDrugWithName detailName = new DiseaseDrugWithName();
			detailName.setSource(String.valueOf(m.get("diseaseName")));
			detailName.setTarget(String.valueOf(m.get("drugName")));
			detailName.setWeight(0.9d);
			detailName.setName("使用");
			linkList.add(detailName);
			DiseaseDrugWithoutName detailName2 = new DiseaseDrugWithoutName();
			detailName2.setTarget(String.valueOf(m.get("diseaseName")));
			detailName2.setSource(String.valueOf(m.get("drugName")));
			detailName2.setWeight(1.0d);
			linkList.add(detailName2);

		});

		//最终结果格式
		DiseaseDrugUnionOutput output = new DiseaseDrugUnionOutput();
		output.setNodes(nodes);
		output.setLinks(linkList);
		//直接返回结果
		return output;

	}

	/**
	 * 根据关键字，查询目标适应症分布的年龄信息
	 *
	 * @param keyword 关键字
	 * @return 目标适应症分布的年龄信息
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> queryDiseaseAgeFromDb(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DiseaseEntity> list = diseaseQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DiseaseEntity::getDiseaseType3).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DISEASE.DISEASE_TYPE13 in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" PRESCRIPTION_DISEASES.AGE as \"age\",PRESCRIPTION_DISEASES.M_SEX as \"sex\",count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.DISEASE as DISEASE" +
				" ON PRESCRIPTION_DISEASES.M_DIAGNOSTIC = DISEASE.DISEASE_TYPE13" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' " +
				" group by PRESCRIPTION_DISEASES.AGE,PRESCRIPTION_DISEASES.M_SEX order by count(0) desc limit 20";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);

	}

	/**
	 * 根据关键词从DB中检索疾病编码，然后通过kylin关联查询科室名称
	 *
	 * @param keyword 用户输入
	 * @return 疾病编码，关联查询科室名称
	 * @throws Exception kylin查询异常
	 */
	public List<Map<String, Object>> queryDiseaseSectionFromDb(String keyword) throws Exception {
		String where = "";
		//用户输入内容，构建查询条件
		if (StringUtils.isNotEmpty(keyword)) {
			//从数据库中检索疾病编码
			List<DiseaseEntity> list = diseaseQueryByKeyword(keyword);
			if (list.isEmpty()) return new ArrayList<>();
			List<String> diseaseCodes = list.stream().map(DiseaseEntity::getDiseaseType3).collect(Collectors.toList());
			//where条件构建
			if (diseaseCodes.size() > 0) {
				where = "and DISEASE.DISEASE_TYPE13 in('" + String.join("','", diseaseCodes) + "')";
			}
		}
		//查询立方体语句
		String sql = "SELECT " +
				" SECTION.SECTION_NAME1 as \"SectionName\",count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES" +
				" LEFT JOIN BIGDATA.SECTION as SECTION" +
				" ON PRESCRIPTION_DISEASES.M_SECTION = SECTION.SECTION2" +
				" LEFT JOIN BIGDATA.DISEASE as DISEASE" +
				" ON PRESCRIPTION_DISEASES.M_DIAGNOSTIC = DISEASE.DISEASE_TYPE13" +
				" LEFT JOIN BIGDATA.DRUG as DRUG" +
				" ON PRESCRIPTION_DISEASES.M_DRUG = DRUG.DRUG" +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA" +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID" +
				" WHERE 1=1 " + where + " and DRUG.DRUG_GENERIC_NAME!='' group by SECTION.SECTION_NAME1 limit 20";
		//执行kylin查询，返回结果
		return beanFactory.getBean(KylinUtil.class).QueryForList(sql);

	}

	/**
	 * 目标适应症-城市等级统计信息
	 *
	 * @return 目标适应症-城市等级统计信息
	 * @throws Exception kylin查询异常
	 */
	public CityLevelTotalOutput cityLevelCompetation() throws Exception {
		//查询立方体语句
		String sql = "SELECT " +
				"CAST(PRESCRIPTION_DISEASES.YEAR_MONTH AS CHAR) as \"year\" " +
				" ,HOSP_AREA.CITY_LEVEL_NAME as \"level\" " +
				" ,sum(PRESCRIPTION_DISEASES.PRICE) as \"price\" " +
				" ,sum(PRESCRIPTION_DISEASES.AMOUNT) as \"amount\", " +
				" count(0) as \"counter\" " +
				"  FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES " +
				" INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA " +
				" ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID " +
				" WHERE 1=1  " +
				" group by PRESCRIPTION_DISEASES.YEAR_MONTH,HOSP_AREA.CITY_LEVEL_NAME " +
				" order by PRESCRIPTION_DISEASES.YEAR_MONTH,HOSP_AREA.CITY_LEVEL_NAME";
		//执行kylin查询
		List<Map<String, Object>> searchResult = beanFactory.getBean(KylinUtil.class).QueryForList(sql);
		List<CityLevelOutput> output = new ArrayList<>();
		for (Map<String, Object> map : searchResult) {
			output.add((CityLevelOutput) MapUtil.mapToBean(map, CityLevelOutput.class));
		}
		//按照接口格式重新排列数据
		CityLevelTotalOutput totalOutput = new CityLevelTotalOutput();
		List<String> yearList = new ArrayList<>();
		List<String> levelList = new ArrayList<>();

		output.forEach(item -> {
			if (!yearList.contains(item.getYear())) {
				yearList.add(item.getYear());
			}
			if (item.getLevel() != null && !levelList.contains(item.getLevel())) {
				levelList.add(item.getLevel());
			}
		});
		//获取年份列表
		totalOutput.setYearData(yearList);
		List<CityLevelTotalDetailOutput> detailList = new ArrayList<CityLevelTotalDetailOutput>();
		levelList.forEach(level -> {
			CityLevelTotalDetailOutput detail = new CityLevelTotalDetailOutput();
			detail.setLevel(level);
			yearList.forEach(year -> {
				if (detail.getBarData() == null) detail.setBarData(new ArrayList<>());
				if (detail.getLineData() == null) detail.setLineData(new ArrayList<>());
				double barData = 0d;
				if (output.stream().filter(m -> m.getLevel() != null && m.getLevel().equals(level) && m.getYear().equals(year))
						.map(CityLevelOutput::getAmount).reduce(Double::sum).isPresent()) {
					barData = output.stream().filter(m -> m.getLevel() != null && m.getLevel().equals(level) && m.getYear().equals(year))
							.map(CityLevelOutput::getAmount).reduce(Double::sum).get();
				}

				if (detail.getBarData().size() > 0) {
					double lineData = 100 * (barData - detail.getBarData().get(detail.getBarData().size() - 1)) / detail.getBarData().get(detail.getBarData().size() - 1);
					detail.getLineData().add(MathsUtil.round(lineData, 0));
				}
				detail.getBarData().add(MathsUtil.round(barData, 0));
			});
			detailList.add(detail);
		});
		//设置每年数据列表
		totalOutput.setCityData(detailList);

		//直接返回结果
		return totalOutput;
	}

	/**
	 * 目标适应症的年龄分布情况
	 *
	 * @return 目标适应症的年龄分布情况
	 * @throws Exception kylin查询异常
	 */
	public AgeOutput ageCount() throws Exception {
		//查询立方体语句
		String sql = "SELECT " +
				"PRESCRIPTION_DISEASES.AGE as \"age\" " +
				",PRESCRIPTION_DISEASES.M_SEX as \"sex\" " +
				",sum(PRESCRIPTION_DISEASES.PRICE) as \"price\" " +
				",sum(PRESCRIPTION_DISEASES.AMOUNT) as \"amount\", " +
				"count(0) as \"counter\" " +
				" FROM BIGDATA.PRESCRIPTION_DISEASES as PRESCRIPTION_DISEASES " +
				"INNER JOIN BIGDATA.HOSP_AREA as HOSP_AREA " +
				"ON PRESCRIPTION_DISEASES.HOSP_ID = HOSP_AREA.HOSP_ID " +
				"WHERE 1=1  " +
				"group by PRESCRIPTION_DISEASES.AGE,PRESCRIPTION_DISEASES.M_SEX " +
				"order by PRESCRIPTION_DISEASES.AGE ";
		//执行kylin查询
		List<Map<String, Object>> searchResult = beanFactory.getBean(KylinUtil.class).QueryForList(sql);
		List<AgeDetailOutput> entityList = new ArrayList<>();
		for (Map<String, Object> map : searchResult) {
			entityList.add((AgeDetailOutput) MapUtil.mapToBean(map, AgeDetailOutput.class));
		}
		List<String> ageRange = new ArrayList<>();
		List<Double> manList = new ArrayList<>();
		List<Double> womanList = new ArrayList<>();
		//获取总条数
		int totalCount = 0;
		if (entityList.stream().map(AgeDetailOutput::getCounter).reduce(Long::sum).isPresent()) {
			totalCount = entityList.stream().map(AgeDetailOutput::getCounter).reduce(Long::sum).get().intValue();
		}

		//获取每个年龄阶段数量
		for (int i = 40; i < 90; i = i + 10) {
			int min = i;
			int max = min + 10;
			ageRange.add(min + "-" + max + "岁");
			if (entityList.stream().filter(m -> m.getAge() >= min && m.getAge() < max && m.getSex().equals("10"))
					.map(AgeDetailOutput::getCounter).reduce(Long::sum).isPresent()) {
				manList.add(MathsUtil.round(entityList.stream().filter(m -> m.getAge() >= min && m.getAge() < max && m.getSex().equals("10"))
						.map(AgeDetailOutput::getCounter).reduce(Long::sum).get() * 100d / totalCount, 1));
			}
			if (entityList.stream().filter(m -> m.getAge() >= min && m.getAge() < max && m.getSex().equals("20"))
					.map(AgeDetailOutput::getCounter).reduce(Long::sum).isPresent()) {
				womanList.add(MathsUtil.round(entityList.stream().filter(m -> m.getAge() >= min && m.getAge() < max && m.getSex().equals("20"))
						.map(AgeDetailOutput::getCounter).reduce(Long::sum).get() * 100d / totalCount, 1));
			}
		}
		AgeOutput output = new AgeOutput();
		output.setAgeRange(ageRange);
		output.setAgeData(new ArrayList<>(Arrays.asList(manList, womanList)));
		//直接返回结果
		return output;
	}

	private List<DiseaseEntity> diseaseQueryByKeyword(String keyword) {
		QueryWrapper<DiseaseEntity> query = new QueryWrapper<>();
		if (StringUtils.isNotBlank(keyword)) query.like("disease_type_name13", keyword);
		return diseaseMapper.selectList(query);
	}
}
