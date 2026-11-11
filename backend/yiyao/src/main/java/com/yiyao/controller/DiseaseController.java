package com.yiyao.controller;

import com.yiyao.output.DiseaseDrugUnionOutput;
import com.yiyao.output.WebResult;
import com.yiyao.service.DiseaseService;
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
}
