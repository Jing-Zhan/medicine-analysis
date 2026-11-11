package com.yiyao.kylin;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Scope;
import org.springframework.stereotype.Component;

import java.sql.*;
import java.util.*;

/**
 * kylin工具类
 */
@Component
@Scope("prototype")
public class KylinUtil {

	@Value("${kylin.driverName}")
	private String driverName;

	@Value("${kylin.url}")
	private String kylinUrl;

	@Value("${kylin.username}")
	private String kylinUser;

	@Value("${kylin.password}")
	private String kylinPassword;

	private Connection conn = null;
	private Statement stmt = null;

	public void init() throws Exception {
		Class.forName(driverName);
		conn = DriverManager.getConnection(kylinUrl, kylinUser, kylinPassword);
		stmt = conn.createStatement();
	}

	public List<Map<String, Object>> QueryForList(String sql) throws Exception {
		List<Map<String, Object>> results = new ArrayList<>();
		try {
			if (conn == null || conn.isClosed()) init();
			ResultSet res = stmt.executeQuery(sql);
			ResultSetMetaData meta = res.getMetaData();
			while (res.next()) {
				Map<String, Object> map = new LinkedHashMap<>();
				for (int i = 1; i <= meta.getColumnCount(); i++) {
					map.put(meta.getColumnLabel(i), res.getObject(i));
				}
				results.add(map);
			}
		} catch (Exception e) {
			System.err.println(e.getMessage());
		} finally {
			if (conn != null) conn.close();
		}
		return results;
	}
}
