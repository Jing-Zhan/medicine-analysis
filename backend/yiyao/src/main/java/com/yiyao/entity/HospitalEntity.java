package com.yiyao.entity;

import lombok.Data;

/**
 * 医院信息
 */
@Data
public class HospitalEntity {

	private Integer hospId;

	private String hospNo;

	private String hospName;

	private String hospAttachedName;

	private String hospGradeName;

	private String hospLevelName;

	private String hospTypeName;
}
