package com.yiyao.output;

import com.yiyao.util.IgnoreConvert;
import lombok.Data;

@Data
@IgnoreConvert
public class DiseaseDrugWithName {

	private String source;

	private String target;

	private Double weight;

	private String name;
}
