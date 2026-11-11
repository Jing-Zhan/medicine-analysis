package com.yiyao.controller;

import com.yiyao.output.WebResult;
import com.yiyao.service.DrugService;
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
}
