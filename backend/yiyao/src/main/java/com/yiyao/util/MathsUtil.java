package com.yiyao.util;

import java.text.DecimalFormat;

public class MathsUtil {

	/**
	 * 保留两位小数
	 *
	 * @param v
	 * @param length
	 * @return
	 */
	public static double round(double v, int length) {
		StringBuilder format = new StringBuilder(".");
		for (int i = 0; i < length; i++) format.append("#");
		DecimalFormat df = new DecimalFormat(format.toString());
		String s = df.format(v);
		return Double.parseDouble(s);
	}
}
