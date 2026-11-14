package com.yiyao.output;

import lombok.Data;

import java.util.List;

/**
 * 适应症画像 / 药品画像 的统一返回结构。
 *
 * 两个方向（疾病→药品、药品→疾病）共用同一个结构，前端一个组件即可复用：
 *   mode      = disease 或 drug，表示本次是哪一侧的画像
 *   target    = 目标对象本身（编码、名称、处方数、金额、占全库比例）
 *   itemLabel = 关联榜的表头文字（关联药品 / 关联适应症）
 *   items     = 关联强度榜，按提升度降序
 *   structure = 结构分布（年龄段占比、科室前五、地区前五）
 *   tags      = 属性标签（基本药物、OTC、特殊管理、妊娠风险；取不到时标注未记录）
 *
 * 注意：响应体会经 DtoJsonConverter 处理，字段名首字母大写，
 * 前端读取 Target / Items / Structure / Tags。
 */
@Data
public class ProfileOutput {

	/**
	 * disease 或 drug
	 */
	private String mode;

	private Target target;

	/**
	 * 关联榜表头
	 */
	private String itemLabel;

	private List<Item> items;

	private Structure structure;

	private List<Tag> tags;

	/**
	 * 目标对象
	 */
	@Data
	public static class Target {
		private String code;
		private String name;
		private long records;
		private double amount;
		/**
		 * 占全库处方数的比例，单位 %
		 */
		private double share;
		/**
		 * 所属疾病大类，仅疾病画像返回
		 */
		private String category;
		/**
		 * 所属疾病中类，仅疾病画像返回
		 */
		private String subCategory;
	}

	/**
	 * 关联强度榜的一行
	 */
	@Data
	public static class Item {
		private String code;
		private String name;
		private long count;
		/**
		 * 置信度：得这个病用这个药的概率，或这个药用于这个病的概率
		 */
		private double conf;
		/**
		 * 提升度：大于 1 表示存在额外倾向
		 */
		private double lift;
	}

	/**
	 * 结构分布
	 */
	@Data
	public static class Structure {
		private List<String> ageRange;
		/**
		 * 与 ageRange 一一对应的比例，单位 %
		 */
		private List<Double> ageShare;
		private List<Group> sections;
		private List<Group> areas;
		/**
		 * 地区维度的表头：疾病画像取省份，药品画像取城市
		 */
		private String areaLabel;
	}

	@Data
	public static class Group {
		private String name;
		private long count;
	}

	@Data
	public static class Tag {
		private String label;
		private String value;
	}
}
