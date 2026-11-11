package com.yiyao;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

@Configuration
public class CorsConfig {

	private CorsConfiguration buildConfig() {
		// 添加CORS配置信息
		CorsConfiguration corsConfiguration = new CorsConfiguration();
		// 放行哪些原始域
		corsConfiguration.addAllowedOrigin("*");
		// 放行哪些头部信息
		corsConfiguration.addAllowedHeader("*");
		// 放行哪些请求方式
		corsConfiguration.addAllowedMethod("*");
		return corsConfiguration;
	}

	@Bean
	public CorsFilter corsFilter() {
		UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
		source.registerCorsConfiguration("/**", this.buildConfig());
		return new CorsFilter(source);
	}
}
