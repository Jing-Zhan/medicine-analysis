package com.yiyao.controller;

import com.yiyao.output.AgeOutput;
import com.yiyao.output.CityLevelTotalOutput;
import com.yiyao.output.OverviewOutput;
import com.yiyao.output.WebResult;
import com.yiyao.service.DiseaseService;
import com.yiyao.service.DrugService;
import com.yiyao.service.OverviewService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * 首页接口
 */
@RestController
@RequestMapping("/home")
public class HomeController {

	/**
	 * 目标适应症接口
	 */
	@Autowired
	private DiseaseService diseaseService;

	/**
	 * 药品接口
	 */
	@Autowired
	private DrugService drugService;

	/**
	 * 首页概览指标接口
	 */
	@Autowired
	private OverviewService overviewService;

	/**
	 * 首页概览 6 个指标卡片
	 */
	@GetMapping("/overview")
	public WebResult<List<OverviewOutput>> overview() {
		try {
			return new WebResult<>(overviewService.overview());
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/citylevel")
	public WebResult<CityLevelTotalOutput> cityLevel() {
		try {
			return new WebResult<>(diseaseService.cityLevelCompetation());
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/age")
	public WebResult<AgeOutput> age() {
		try {
			return new WebResult<>(diseaseService.ageCount());
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/top10")
	public WebResult<List<Map<String, Object>>> top10() {
		try {
			return new WebResult<>(drugService.top10amount());
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}

	@GetMapping("/province")
	public WebResult<List<Map<String, Object>>> provinceTotal() {
		try {
			//调用接口返回
			return new WebResult<>(drugService.provinceTotal());
		} catch (Exception e) {
			e.printStackTrace();
			//返回异常结果
			return new WebResult(e);
		}
	}
}
