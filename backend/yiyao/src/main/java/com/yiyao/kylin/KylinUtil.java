package com.yiyao.kylin;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import java.sql.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 查询网关：统一封装「拿一条 SQL 去查出数据」这件事。
 *
 * 支持两种引擎，由配置项 query.engine 控制：
 *   kylin —— 查 Kylin 立方体（默认，符合实训资料的架构）
 *   mysql —— 查 MySQL 明细库（用于需要在药品、诊断等高基数字段上做多表关联的查询）
 *
 * 切到 mysql 时会自动把 Kylin 方言的 SQL 改写成 MySQL 方言，因此
 * 24 处 SQL 语句和 12 个 Service 方法都不需要改：
 *
 *   BIGDATA.PRESCRIPTION_DISEASES → prescription_diseases
 *   BIGDATA.SECTION               → t_view_section
 *   BIGDATA.DISEASE               → t_view_disease
 *   BIGDATA.DRUG                  → t_view_drug
 *   BIGDATA.HOSPITAL              → t_view_hosp
 *   BIGDATA.HOSP_AREA             → t_view_areas
 *   M_DIAGNOSTIC                  → m_diagnostic1   （MySQL 里这一列的列名不同）
 *   M_DRUG = DRUG.DRUG            → DRUG_CODE = DRUG.DRUG
 *       （明细表里药品码形如 DM0000178036_2，维表里是 DM0000178036，
 *         MySQL 侧用一个生成列 drug_code 去掉后缀并建索引，保证关联走索引）
 */
@Component
@Scope("prototype")
public class KylinUtil {

	// ---------------------------------------------------------------- Kylin 配置

	@Value("${kylin.driverName}")
	private String driverName;

	@Value("${kylin.url}")
	private String kylinUrl;

	@Value("${kylin.username}")
	private String kylinUser;

	@Value("${kylin.password}")
	private String kylinPassword;

	// ---------------------------------------------------------------- MySQL 配置

	@Value("${spring.datasource.driverClassName:com.mysql.cj.jdbc.Driver}")
	private String mysqlDriver;

	@Value("${spring.datasource.url}")
	private String mysqlUrl;

	@Value("${spring.datasource.username}")
	private String mysqlUser;

	@Value("${spring.datasource.password}")
	private String mysqlPassword;

	// ---------------------------------------------------------------- 引擎开关

	/**
	 * kylin（默认）或 mysql
	 */
	@Value("${query.engine:kylin}")
	private String engine;

	private Connection conn = null;
	private Statement stmt = null;

	/**
	 * 是否走 MySQL
	 */
	private boolean useMysql() {
		return "mysql".equalsIgnoreCase(String.valueOf(engine).trim());
	}

	public void init() throws Exception {
		if (useMysql()) {
			Class.forName(mysqlDriver);
			conn = DriverManager.getConnection(mysqlUrl, mysqlUser, mysqlPassword);
		} else {
			Class.forName(driverName);
			conn = DriverManager.getConnection(kylinUrl, kylinUser, kylinPassword);
		}
		stmt = conn.createStatement();
		stmt.setQueryTimeout(300);
	}

	/**
	 * 执行查询，返回每行一个 Map（列名 → 值）
	 *
	 * @param sql Kylin 方言的 SQL
	 * @return 结果列表
	 */
	public List<Map<String, Object>> QueryForList(String sql) throws Exception {
		List<Map<String, Object>> results = new ArrayList<>();
		try {
			if (conn == null || conn.isClosed()) init();
			String finalSql = useMysql() ? toMysqlSql(sql) : sql;
			ResultSet res = stmt.executeQuery(finalSql);
			ResultSetMetaData meta = res.getMetaData();
			while (res.next()) {
				Map<String, Object> map = new LinkedHashMap<>();
				for (int i = 1; i <= meta.getColumnCount(); i++) {
					map.put(meta.getColumnLabel(i), res.getObject(i));
				}
				results.add(map);
			}
		} catch (Exception e) {
			System.err.println("[QueryForList] " + e.getMessage());
			throw e;
		} finally {
			if (conn != null) conn.close();
		}
		return results;
	}

	// ---------------------------------------------------------------- SQL 改写

	/**
	 * Kylin 表名 → MySQL 表名。顺序有讲究：
	 * 先换更长的名字，避免 HOSPITAL 被 HOSP_AREA 之类的前缀误伤。
	 */
	private static final String[][] TABLE_MAP = {
			{"BIGDATA.PRESCRIPTION_DISEASES", "prescription_diseases"},
			{"BIGDATA.HOSP_AREA", "t_view_areas"},
			{"BIGDATA.HOSPITAL", "t_view_hosp"},
			{"BIGDATA.SECTION", "t_view_section"},
			{"BIGDATA.DISEASE", "t_view_disease"},
			{"BIGDATA.DRUG", "t_view_drug"},
	};

	/**
	 * 药品码关联：M_DRUG = DRUG.DRUG （左边可能带表名限定）
	 */
	private static final Pattern DRUG_JOIN = Pattern.compile(
			"(?:([A-Za-z_][A-Za-z0-9_]*)\\.)?M_DRUG\\s*=\\s*DRUG\\.DRUG",
			Pattern.CASE_INSENSITIVE);

	/**
	 * 把 Kylin 方言的 SQL 改写成 MySQL 方言
	 *
	 * @param sql 原始 SQL
	 * @return 可直接在 MySQL 执行的 SQL
	 */
	public static String toMysqlSql(String sql) {
		if (sql == null) return null;
		String s = sql;

		// ① 表名
		for (String[] pair : TABLE_MAP) {
			s = s.replace(pair[0], pair[1]);
		}

		// ② M_DRUG = DRUG.DRUG  →  限定名.DRUG_CODE = DRUG.DRUG
		Matcher m = DRUG_JOIN.matcher(s);
		StringBuffer sb = new StringBuffer();
		while (m.find()) {
			String qualifier = m.group(1);
			String lhs = (qualifier == null ? "" : qualifier + ".") + "DRUG_CODE";
			m.appendReplacement(sb, Matcher.quoteReplacement(lhs + " = DRUG.DRUG"));
		}
		m.appendTail(sb);
		s = sb.toString();

		// ③ 诊断列名：M_DIAGNOSTIC → m_diagnostic1
		//    用词边界，避免把 M_DIAGNOSTIC2 / M_DIAGNOSTIC3 也换掉
		s = s.replaceAll("(?i)\\bM_DIAGNOSTIC\\b", "m_diagnostic1");

		return s;
	}
}
