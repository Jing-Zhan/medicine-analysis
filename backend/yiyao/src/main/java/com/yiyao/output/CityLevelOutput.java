package com.yiyao.output;

import lombok.Data;

/**
 * 城市等级
 */
@Data
public class CityLevelOutput {

	private String year;

	private String level;

	private Double price;

	private Double amount;

	private Long counter;
}
