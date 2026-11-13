package com.yiyao.output;

import com.yiyao.util.IgnoreConvert;
import lombok.Data;

/**
 * 首页概览指标卡片。
 *
 * 注意：字段名必须是【小写】label / value / unit。
 * 前端 overview.vue 是按 item.label、item.value、item.unit 读取的，
 * 而 ResponseBodyHandler 里的 DtoJsonConverter 会把 Map 的 key 首字母大写，
 * 因此这里加 @IgnoreConvert 跳过转换，让 Jackson 直接按小写字段名序列化。
 */
@Data
@IgnoreConvert
public class OverviewOutput {

	/**
	 * 指标名称，如「处方总数」
	 */
	private String label;

	/**
	 * 指标数值
	 */
	private Object value;

	/**
	 * 单位，如「条」「元」「家」
	 */
	private String unit;

	public OverviewOutput() {
	}

	public OverviewOutput(String label, Object value, String unit) {
		this.label = label;
		this.value = value;
		this.unit = unit;
	}
}
