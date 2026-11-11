package com.yiyao.config;

import com.yiyao.output.WebResult;
import com.yiyao.util.MapUtil;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

@RestControllerAdvice
public class ResponseBodyHandler implements ResponseBodyAdvice {

	@Override
	public boolean supports(MethodParameter methodParameter, Class aClass) {
		return true;
	}

	@Override
	public Object beforeBodyWrite(Object data, MethodParameter methodParam, MediaType mediaType, Class aClass, ServerHttpRequest serverHttpRequest, ServerHttpResponse serverHttpResponse) {
		if (methodParam.hasMethodAnnotation(ExceptionHandler.class)) return data;
		if (methodParam.getParameterType().equals(WebResult.class)) {
			WebResult result = (WebResult) data;
			result.setData(new MapUtil.DtoJsonConverter().convert(result.getData()));
			return result;
		}
		return data;
	}
}
