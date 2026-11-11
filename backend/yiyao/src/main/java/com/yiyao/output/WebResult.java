package com.yiyao.output;

import lombok.Data;

@Data
public class WebResult<T> {

	/**
	 * 编码，0或200：成功，1失败
	 */
	private Integer code;

	/**
	 * 返回数据
	 */
	private T data;

	private String msg;

	private Boolean success;

	/**
	 * 构造函数
	 * @param t 要返回的数据
	 */
	public WebResult(T t){
		if(t instanceof Exception){
			this.setCode(1);
			this.setMsg(((Exception)t).getMessage());
		} else{
			this.setCode(200);
		}
		this.setData(t);
	}
}
