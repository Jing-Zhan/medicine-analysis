package com.yiyao.service;

import com.yiyao.mapper.StructureMapper;
import com.yiyao.output.StructureRow;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 用药结构对比服务。
 *
 * 把预聚合表里按药品编码记录的处方数，按科室或疾病大类折算成三个结构占比，
 * 输出一张可直接对比的表。
 */
@Service
public class StructureService {

	/** 默认返回条数 */
	private static final int DEFAULT_LIMIT = 10;

	/** 可返回的最大条数 */
	private static final int MAX_LIMIT = 30;

	@Autowired
	private StructureMapper structureMapper;

	/**
	 * 科室用药结构对比。
	 *
	 * @param limit 返回条数，按处方数倒序取前 N 个科室
	 */
	public List<StructureRow> sectionStructure(int limit) {
		return convert(structureMapper.sectionStructure(normalize(limit)));
	}

	/**
	 * 疾病大类用药结构对比。
	 *
	 * @param limit 返回条数，按处方数倒序取前 N 个疾病大类
	 */
	public List<StructureRow> categoryStructure(int limit) {
		return convert(structureMapper.categoryStructure(normalize(limit)));
	}

	private int normalize(int limit) {
		if (limit <= 0) {
			return DEFAULT_LIMIT;
		}
		return Math.min(limit, MAX_LIMIT);
	}

	private List<StructureRow> convert(List<Map<String, Object>> raw) {
		List<StructureRow> rows = new ArrayList<>();
		if (raw == null) {
			return rows;
		}
		for (Map<String, Object> item : raw) {
			long records = toLong(item.get("records"));
			StructureRow row = new StructureRow();
			row.setName(item.get("name") == null ? "未标注" : String.valueOf(item.get("name")));
			row.setRecords(records);
			row.setInjRate(rate(item.get("inj"), records));
			row.setEssRate(rate(item.get("ess"), records));
			row.setAntiRate(rate(item.get("anti"), records));
			rows.add(row);
		}
		return rows;
	}

	private long toLong(Object value) {
		if (value instanceof Number) {
			return ((Number) value).longValue();
		}
		if (value == null) {
			return 0L;
		}
		try {
			return Long.parseLong(String.valueOf(value));
		} catch (NumberFormatException e) {
			return 0L;
		}
	}

	private double rate(Object value, long total) {
		if (total <= 0) {
			return 0D;
		}
		long part = toLong(value);
		return Math.round(part * 10000.0 / total) / 100.0D;
	}
}
