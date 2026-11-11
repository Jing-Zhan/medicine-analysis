package com.yiyao.entity;

import lombok.Data;

/**
 * 疾病-药品关系表
 */
@Data
public class PrescriptionDiseaseEntity {

	private String recordId;

	private String fileId;

	private Integer hospId;

	private Integer dataType;

	private Integer yearMonth;

	private Double price;

	private Double amount;

	private Integer age;

	private String sex;

	private String mSection;

	private String mDrug;

	private String mDiagnostic;
}
