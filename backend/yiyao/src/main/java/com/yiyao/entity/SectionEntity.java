package com.yiyao.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 科室信息
 */
@Data
@TableName("t_view_section")
public class SectionEntity {

	@TableField("section2")
	private String section2;

	@TableField("section_name2")
	private String sectionName2;

	@TableField("section1")
	private String section1;

	@TableField("section_name1")
	private String sectionName1;
}
