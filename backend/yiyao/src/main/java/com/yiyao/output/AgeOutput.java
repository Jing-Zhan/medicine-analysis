package com.yiyao.output;

import lombok.Data;

import java.util.List;

@Data
public class AgeOutput {

	private List<String> ageRange;

	private List<List<Double>> ageData;
}
