package com.yiyao.output;

import lombok.Data;

import java.util.List;

@Data
public class CityLevelTotalOutput {

	private List<String> yearData;

	private List<CityLevelTotalDetailOutput> cityData;
}
