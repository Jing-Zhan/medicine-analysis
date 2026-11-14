package com.yiyao.output;

/**
 * 用药结构对比表中的一行。
 *
 * 这份数据的价格基本恒定，费用类指标没有区分度，因此这里只输出处方数与三个
 * 结构占比：注射剂、基本药物、抗菌药物。占比单位为百分数，保留两位小数。
 */
public class StructureRow {

	/** 维度取值，科室名或疾病大类名 */
	private String name;

	/** 处方数，按该维度汇总 */
	private long records;

	/** 注射剂占比，百分数 */
	private double injRate;

	/** 基本药物占比，百分数 */
	private double essRate;

	/** 抗菌药物占比，百分数 */
	private double antiRate;

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public long getRecords() {
		return records;
	}

	public void setRecords(long records) {
		this.records = records;
	}

	public double getInjRate() {
		return injRate;
	}

	public void setInjRate(double injRate) {
		this.injRate = injRate;
	}

	public double getEssRate() {
		return essRate;
	}

	public void setEssRate(double essRate) {
		this.essRate = essRate;
	}

	public double getAntiRate() {
		return antiRate;
	}

	public void setAntiRate(double antiRate) {
		this.antiRate = antiRate;
	}
}
