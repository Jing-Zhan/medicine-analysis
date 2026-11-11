package com.yiyao.output;

import lombok.Data;

import java.util.List;

@Data
public class CityLevelTotalDetailOutput {

	private String level;

	private List<Double> barData;

	private List<Double> lineData;
}
