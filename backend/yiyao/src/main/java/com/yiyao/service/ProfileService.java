package com.yiyao.service;

import com.yiyao.mapper.ProfileMapper;
import com.yiyao.output.ProfileOutput;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

/**
 * 适应症画像与药品画像。
 *
 * 与其余 13 个接口的区别：那些接口输出描述性统计（谁多用、谁排前），
 * 这里输出关联强度，用来区分「因为量大」和「因为对该适应症确实专用」。
 *
 * 三个统计量的口径（N 为全库处方数）：
 *   support = cnt / N
 *   conf    = cnt / 目标对象的处方数
 *   lift    = conf / (对照对象的处方数 / N)
 *
 * 预计算表已经把 cnt、两个分母、N 都放在同一行，因此这里只做四则运算，
 * 不再访问明细表。
 */
@Service
public class ProfileService {

	/**
	 * 组合次数低于该值时不计入关联榜，避免小样本把提升度推高
	 */
	private static final int MIN_COUNT = 20;

	/**
	 * 关联榜取前多少条
	 */
	private static final int TOP_N = 10;

	/**
	 * 年龄段划分起点与段数，与首页年龄图保持一致
	 */
	private static final int AGE_START = 40;
	private static final int AGE_STEP = 10;
	private static final int AGE_BUCKETS = 5;

	@Autowired
	private ProfileMapper mapper;

	// ---------------------------------------------------------------- 疾病画像

	public ProfileOutput diseaseProfile(String code, String keyword) {
		Map<String, Object> target = resolveDisease(code, keyword);
		if (target == null) {
			throw new IllegalArgumentException("未找到匹配的适应症：" + (isEmpty(code) ? keyword : code));
		}
		String targetCode = str(target.get("code"));
		long grand = mapper.grandTotal();

		ProfileOutput out = new ProfileOutput();
		out.setMode("disease");
		out.setTarget(toTarget(target, grand));
		out.setItemLabel("关联药品");

		// 关联强度榜：对照对象的处方数放在 var_total
		List<Map<String, Object>> rows = mapper.drugsOfDisease(targetCode, MIN_COUNT);
		out.setItems(toItems(rows));

		// 结构分布
		ProfileOutput.Structure st = new ProfileOutput.Structure();
		fillAge(st, mapper.ageOfDisease(targetCode));
		st.setSections(toGroups(mapper.sectionsOfDisease(targetCode)));
		st.setAreas(toGroups(mapper.provincesOfDisease(targetCode)));
		st.setAreaLabel("省份");
		out.setStructure(st);

		// 属性标签：该适应症用药里基本药物与 OTC 的构成
		List<ProfileOutput.Tag> tags = new ArrayList<>();
		tags.add(dominantTag("基本药物", mapper.essentialOfDisease(targetCode)));
		tags.add(dominantTag("非处方药", mapper.otcOfDisease(targetCode)));
		out.setTags(tags);
		return out;
	}

	// ---------------------------------------------------------------- 药品画像

	public ProfileOutput drugProfile(String code, String keyword) {
		Map<String, Object> target = resolveDrug(code, keyword);
		if (target == null) {
			throw new IllegalArgumentException("未找到匹配的药品：" + (isEmpty(code) ? keyword : code));
		}
		String targetCode = str(target.get("code"));
		long grand = mapper.grandTotal();

		ProfileOutput out = new ProfileOutput();
		out.setMode("drug");
		out.setTarget(toTarget(target, grand));
		out.setItemLabel("关联适应症");

		List<Map<String, Object>> rows = mapper.diseasesOfDrug(targetCode, MIN_COUNT);
		out.setItems(toItems(rows));

		ProfileOutput.Structure st = new ProfileOutput.Structure();
		fillAge(st, mapper.ageOfDrug(targetCode));
		st.setSections(toGroups(mapper.sectionsOfDrug(targetCode)));
		st.setAreas(toGroups(mapper.citiesOfDrug(targetCode)));
		st.setAreaLabel("城市");
		out.setStructure(st);

		List<ProfileOutput.Tag> tags = new ArrayList<>();
		tags.add(firstValueTag("基本药物", mapper.essentialOfDrug(targetCode)));
		tags.add(firstValueTag("非处方药", mapper.otcOfDrug(targetCode)));
		tags.add(firstValueTag("特殊管理", mapper.specialOfDrug(targetCode)));
		tags.add(firstValueTag("妊娠风险", mapper.pregnancyOfDrug(targetCode)));
		out.setTags(tags);
		return out;
	}

	// ---------------------------------------------------------------- 目标对象解析

	private Map<String, Object> resolveDisease(String code, String keyword) {
		if (!isEmpty(code)) {
			Map<String, Object> byCode = mapper.diseaseByCode(code.trim());
			if (byCode != null) {
				return byCode;
			}
		}
		if (!isEmpty(keyword)) {
			Map<String, Object> byKeyword = mapper.diseaseByKeyword(keyword.trim());
			if (byKeyword != null) {
				return byKeyword;
			}
		}
		// 不传参数时默认选中处方量最大的适应症，保证页面初次打开有内容
		return mapper.topDisease();
	}

	private Map<String, Object> resolveDrug(String code, String keyword) {
		if (!isEmpty(code)) {
			Map<String, Object> byCode = mapper.drugByCode(code.trim());
			if (byCode != null) {
				return byCode;
			}
		}
		if (!isEmpty(keyword)) {
			Map<String, Object> byKeyword = mapper.drugByKeyword(keyword.trim());
			if (byKeyword != null) {
				return byKeyword;
			}
		}
		// 不传参数时默认选中处方量最大的药品
		return mapper.topDrug();
	}

	private ProfileOutput.Target toTarget(Map<String, Object> row, long grand) {
		ProfileOutput.Target t = new ProfileOutput.Target();
		t.setCode(str(row.get("code")));
		t.setName(str(row.get("name")));
		t.setRecords(toLong(row.get("records")));
		t.setAmount(round2(toDouble(row.get("amount"))));
		t.setShare(grand > 0 ? round2(toLong(row.get("records")) * 100.0 / grand) : 0D);
		return t;
	}

	// ---------------------------------------------------------------- 关联榜计算

	/**
	 * 由组合明细算出置信度与提升度，按提升度降序取前十。
	 * 每行的 fix_total 是目标对象的处方数，var_total 是对照对象的处方数。
	 */
	private List<ProfileOutput.Item> toItems(List<Map<String, Object>> rows) {
		List<ProfileOutput.Item> list = new ArrayList<>();
		if (rows == null) {
			return list;
		}
		long grand = mapper.grandTotal();
		for (Map<String, Object> row : rows) {
			long cnt = toLong(row.get("cnt"));
			long fixTotal = toLong(row.get("fix_total"));
			long varTotal = toLong(row.get("var_total"));
			if (cnt <= 0 || fixTotal <= 0 || varTotal <= 0 || grand <= 0) {
				continue;
			}
			double conf = (double) cnt / fixTotal;
			double base = (double) varTotal / grand;
			double lift = base > 0 ? conf / base : 0D;

			ProfileOutput.Item item = new ProfileOutput.Item();
			item.setCode(str(row.get("code")));
			item.setName(str(row.get("name")));
			item.setCount(cnt);
			item.setConf(round4(conf));
			item.setLift(round3(lift));
			list.add(item);
		}
		list.sort(Comparator.comparingDouble(ProfileOutput.Item::getLift).reversed()
				.thenComparing(Comparator.comparingLong(ProfileOutput.Item::getCount).reversed()));
		return list.size() > TOP_N ? new ArrayList<>(list.subList(0, TOP_N)) : list;
	}

	// ---------------------------------------------------------------- 结构分布

	/**
	 * 年龄按固定十岁分段，分母为该目标对象的全部处方数
	 */
	private void fillAge(ProfileOutput.Structure st, List<Map<String, Object>> rows) {
		List<String> labels = new ArrayList<>();
		List<Double> shares = new ArrayList<>();
		for (int i = 0; i < AGE_BUCKETS; i++) {
			labels.add((AGE_START + i * AGE_STEP) + "-" + (AGE_START + (i + 1) * AGE_STEP) + "岁");
			shares.add(0D);
		}
		long total = 0L;
		long[] counts = new long[AGE_BUCKETS];
		if (rows != null) {
			for (Map<String, Object> row : rows) {
				long age = toLong(row.get("k"));
				long c = toLong(row.get("c"));
				total += c;
				int idx = (int) ((age - AGE_START) / AGE_STEP);
				if (idx >= 0 && idx < AGE_BUCKETS) {
					counts[idx] += c;
				}
			}
		}
		if (total > 0) {
			for (int i = 0; i < AGE_BUCKETS; i++) {
				shares.set(i, round2(counts[i] * 100.0 / total));
			}
		}
		st.setAgeRange(labels);
		st.setAgeShare(shares);
	}

	private List<ProfileOutput.Group> toGroups(List<Map<String, Object>> rows) {
		List<ProfileOutput.Group> list = new ArrayList<>();
		if (rows == null) {
			return list;
		}
		for (Map<String, Object> row : rows) {
			ProfileOutput.Group g = new ProfileOutput.Group();
			g.setName(str(row.get("name")));
			g.setCount(toLong(row.get("cnt")));
			list.add(g);
		}
		return list;
	}

	// ---------------------------------------------------------------- 属性标签

	/**
	 * 药品维度：该药的属性直接取一列，取不到则标注未记录
	 */
	private ProfileOutput.Tag firstValueTag(String label, List<Map<String, Object>> rows) {
		ProfileOutput.Tag tag = new ProfileOutput.Tag();
		tag.setLabel(label);
		tag.setValue("未记录");
		if (rows != null && !rows.isEmpty()) {
			String v = str(rows.get(0).get("v")).trim();
			if (!isEmpty(v) && !"-".equals(v) && !"\\N".equals(v)) {
				tag.setValue(v);
			}
		}
		return tag;
	}

	/**
	 * 适应症维度：取占比最高的取值并附上比例，例如「是 82.3%」
	 */
	private ProfileOutput.Tag dominantTag(String label, List<Map<String, Object>> rows) {
		ProfileOutput.Tag tag = new ProfileOutput.Tag();
		tag.setLabel(label);
		tag.setValue("未记录");
		if (rows == null || rows.isEmpty()) {
			return tag;
		}
		long total = 0L;
		for (Map<String, Object> row : rows) {
			total += toLong(row.get("c"));
		}
		Map<String, Object> top = rows.get(0);
		String v = str(top.get("v")).trim();
		if (isEmpty(v) || "-".equals(v) || "\\N".equals(v)) {
			v = "未记录";
		}
		long c = toLong(top.get("c"));
		if (total > 0) {
			tag.setValue(v + "　" + round2(c * 100.0 / total) + "%");
		} else {
			tag.setValue(v);
		}
		return tag;
	}

	// ---------------------------------------------------------------- 工具

	private static boolean isEmpty(String s) {
		return s == null || s.trim().length() == 0;
	}

	private static String str(Object v) {
		return v == null ? "" : String.valueOf(v);
	}

	private static long toLong(Object v) {
		if (v == null) {
			return 0L;
		}
		if (v instanceof Number) {
			return ((Number) v).longValue();
		}
		try {
			return Long.parseLong(String.valueOf(v).trim());
		} catch (NumberFormatException e) {
			return 0L;
		}
	}

	private static double toDouble(Object v) {
		if (v == null) {
			return 0D;
		}
		if (v instanceof Number) {
			return ((Number) v).doubleValue();
		}
		try {
			return Double.parseDouble(String.valueOf(v).trim());
		} catch (NumberFormatException e) {
			return 0D;
		}
	}

	private static double round2(double v) {
		return Math.round(v * 100D) / 100D;
	}

	private static double round3(double v) {
		return Math.round(v * 1000D) / 1000D;
	}

	private static double round4(double v) {
		return Math.round(v * 10000D) / 10000D;
	}
}
