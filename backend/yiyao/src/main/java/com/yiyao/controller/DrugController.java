package com.yiyao.controller;

import com.yiyao.output.ProfileOutput;
import com.yiyao.output.StructureRow;
import com.yiyao.output.WebResult;
import com.yiyao.service.DrugService;
import com.yiyao.service.ProfileService;
import com.yiyao.service.StructureService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * 药品分析接口
 */
@RestController
@RequestMapping("/drug")
public class DrugController {

	/**
	 * 药品接口
	 */
	@Autowired
	private DrugService drugService;

	/**
	 * 画像接口
	 */
	@Autowired
	private ProfileService profileService;

	/**
	 * 用药结构对比接口
	 */
	@Autowired
	private StructureService structureService;

	/**
	 * 药品品牌覆盖城市
	 */
	@GetMapping("/cities")
	public WebResult<List<Map<String, Object>>> drugCity(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(drugService.queryCities(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	/**
	 * 药品品牌覆盖医院分析
	 */
	@GetMapping("/hospital")
	public WebResult<List<Map<String, Object>>> drugHospital(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(drugService.queryHospitals(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	/**
	 * 目标药品对应适应症
	 */
	@GetMapping("/diseases")
	public WebResult<List<Map<String, Object>>> drugDiseases(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(drugService.queryDiseases(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	/**
	 * 药品对应科室分布
	 */
	@GetMapping("/section")
	public WebResult<List<Map<String, Object>>> drugSection(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(drugService.querySections(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	/**
	 * 药品侧总览：合理用药指标与厂商份额、市场集中度。
	 */
	@GetMapping("/overview")
	public WebResult<Map<String, Object>> drugOverview() {
		try {
			return new WebResult<>(profileService.drugOverview());
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}

	/**
	 * 药品属性构成。
	 *
	 * @param type  form_name1 剂型、is_essential_drug 基本药物、is_otc 非处方药、
	 *              is_special_drug 特殊管理、risk_pregnancy_grade 妊娠风险
	 * @param limit 返回条数，上限 30
	 */
	@GetMapping("/attribute")
	public WebResult<List<Map<String, Object>>> drugAttribute(
			@RequestParam(defaultValue = "form_name1") String type,
			@RequestParam(defaultValue = "15") int limit) {
		try {
			return new WebResult<>(profileService.drugComposition(type, limit));
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}

	/**
	 * 科室用药结构对比。
	 *
	 * 按处方数取前 N 个科室，输出注射剂、基本药物、抗菌药物三个占比，
	 * 用来观察不同科室的用药结构差异。
	 *
	 * @param limit 返回条数，上限 30
	 */
	@GetMapping("/structure")
	public WebResult<List<StructureRow>> drugStructure(@RequestParam(defaultValue = "10") int limit) {
		try {
			return new WebResult<>(structureService.sectionStructure(limit));
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}

	/**
	 * 药品画像。
	 *
	 * 与上面四个接口的区别：那些接口输出描述性统计，这里输出该药品的适应症谱，
	 * 按提升度排序，用来回答「这个药主要治什么、还对哪些适应症有额外倾向」。
	 *
	 * @param code    药品编码，优先使用
	 * @param keyword 关键词，编码为空时按通用名模糊匹配并取处方量最大的一条
	 */
	@GetMapping("/profile")
	public WebResult<ProfileOutput> drugProfile(@RequestParam(required = false) String code,
												@RequestParam(required = false) String keyword) {
		try {
			return new WebResult<>(profileService.drugProfile(code, keyword));
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}
}
