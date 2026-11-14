package com.yiyao.controller;

import com.yiyao.output.DiseaseDrugUnionOutput;
import com.yiyao.output.ProfileOutput;
import com.yiyao.output.WebResult;
import com.yiyao.service.DiseaseService;
import com.yiyao.service.ProfileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * 目标适应症接口
 */
@RestController
@RequestMapping("/disease")
public class DiseaseController {

	@Autowired
	private DiseaseService diseaseService;

	@Autowired
	private ProfileService profileService;

	/**
	 * 页面请求目标适应症关联药品组合分析数据
	 */
	@GetMapping("/union")
	public WebResult<List<Map<String, Object>>> diseaseDrugUnion(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(diseaseService.queryDiseaseFromDb(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/drug")
	public WebResult<DiseaseDrugUnionOutput> diseaseUnionDrug(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(diseaseService.queryDiseaseDrugFromDb(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/age")
	public WebResult<List<Map<String, Object>>> diseaseDrugAge(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(diseaseService.queryDiseaseAgeFromDb(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/section")
	public WebResult<List<Map<String, Object>>> diseaseSection(@RequestParam(required = false) String keyword) {
		try {
			//调用接口返回
			return new WebResult<>(diseaseService.queryDiseaseSectionFromDb(keyword));
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	/**
	 * 疾病费用负担。给出总金额与均次费用，用来区分「人多」与「花钱多」。
	 *
	 * @param level 11 大类、12 中类、13 细目
	 * @param limit 返回条数，上限 30
	 */
	@GetMapping("/burden")
	public WebResult<List<Map<String, Object>>> diseaseBurden(
			@RequestParam(defaultValue = "11") int level,
			@RequestParam(defaultValue = "10") int limit) {
		try {
			return new WebResult<>(profileService.diseaseBurden(level, limit));
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}

	/**
	 * 疾病分层构成。
	 *
	 * @param level 11 大类、12 中类、13 细目
	 * @param limit 返回条数，上限 30
	 */
	@GetMapping("/category")
	public WebResult<List<Map<String, Object>>> diseaseCategory(
			@RequestParam(defaultValue = "11") int level,
			@RequestParam(defaultValue = "15") int limit) {
		try {
			return new WebResult<>(profileService.diseaseComposition(level, limit));
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}

	/**
	 * 目标适应症画像。
	 *
	 * 与上面四个接口的区别：那些接口输出描述性统计，这里输出关联强度，
	 * 用提升度区分「因为量大」与「对该适应症确实专用」。
	 *
	 * @param code    适应症编码，优先使用
	 * @param keyword 关键词，编码为空时按名称模糊匹配并取处方量最大的一条
	 */
	@GetMapping("/profile")
	public WebResult<ProfileOutput> diseaseProfile(@RequestParam(required = false) String code,
												  @RequestParam(required = false) String keyword) {
		try {
			return new WebResult<>(profileService.diseaseProfile(code, keyword));
		} catch (Exception e) {
			e.printStackTrace();
			return new WebResult(e);
		}
	}
}
