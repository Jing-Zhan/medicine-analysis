package com.yiyao.output;

import lombok.Data;

import java.util.List;

@Data
public class DiseaseDrugUnionOutput {

	private List<DiseaseDrugNode> nodes;

	private List<Object> links;
}
