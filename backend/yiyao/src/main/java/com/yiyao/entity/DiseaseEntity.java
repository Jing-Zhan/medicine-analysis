package com.yiyao.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 疾病信息
 */
@Data
@TableName("t_view_disease")
public class DiseaseEntity {

	@TableField("disease_type13")
	private String diseaseType3;

	@TableField("disease_type_name13")
	private String diseaseTypeName3;

	@TableField("disease_type12")
	private String diseaseType2;

	@TableField("disease_type_name12")
	private String diseaseTypeName2;

	@TableField("disease_type11")
	private String diseaseType1;

	@TableField("disease_type_name11")
	private String diseaseTypeName1;
}
