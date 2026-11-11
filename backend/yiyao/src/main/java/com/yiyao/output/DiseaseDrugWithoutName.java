package com.yiyao.output;

import com.yiyao.util.IgnoreConvert;
import lombok.Data;

@Data
@IgnoreConvert
public class DiseaseDrugWithoutName {

	protected String source;

	protected String target;

	protected Double weight;
}
