package com.yiyao.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 药品信息
 */
@Data
@TableName("t_view_drug")
public class DrugEntity {

	@TableField("drug")
	private String drug;

	@TableField("package_chinese_name")
	private String packageChineseName;

	@TableField("drug_generic_name")
	private String drugGenericName;

	@TableField("drug_trade_name")
	private String drugTradeName;

	@TableField("spec")
	private String spec;

	@TableField("spec_office")
	private String specOffice;

	@TableField("form_name2")
	private String formName2;

	@TableField("form_name2")
	private String formName1;
}
