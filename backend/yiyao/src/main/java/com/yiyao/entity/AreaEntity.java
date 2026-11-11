package com.yiyao.entity;

import lombok.Data;

/**
 * 区域信息
 */
@Data
public class AreaEntity {
	private Integer hospId;

	private Integer city;

	private String cityName;

	private String cityTypeName;

	private String cityLevelName;

	private String province;

	private String provinceName;

	private String economicRegionName;

	private String administrativeName;
}
