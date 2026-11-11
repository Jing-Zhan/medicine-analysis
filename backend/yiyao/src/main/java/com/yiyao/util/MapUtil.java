package com.yiyao.util;

import java.beans.BeanInfo;
import java.beans.Introspector;
import java.beans.PropertyDescriptor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.*;

/**
 * Map转换类
 */
public class MapUtil {

	public static void mapToBean(Map<String, Object> map, Object obj) throws Exception {
		BeanInfo beanInfo = Introspector.getBeanInfo(obj.getClass());
		PropertyDescriptor[] propertyDescriptors = beanInfo.getPropertyDescriptors();
		for (PropertyDescriptor property : propertyDescriptors) {
			String key = property.getName();
			if (key.compareToIgnoreCase("class") == 0) continue;
			if (map.containsKey(key)) {
				Object value = map.get(key);
				Method setter = property.getWriteMethod();
				if (setter != null) setter.invoke(obj, value);
			}
		}
	}

	public static Object mapToBean(Map<String, Object> map, Class<?> cls) throws Exception {
		Object obj = cls.newInstance();
		mapToBean(map, obj);
		return obj;
	}

	public static class DtoJsonConverter {
		public Object convert(Object data) {
			if (data == null) {
				return null;
			}
			Class aclass = data.getClass();

			if (data instanceof java.util.List || aclass.isArray()) {
				List<Object> arr = aclass.isArray() ? Arrays.asList((Object[]) data) : (List<Object>) data;
				List<Object> newList = new ArrayList<>();
				arr.forEach(m -> {
					newList.add(convert(m));
				});
				return newList;
			} else {
				return convertObject(data);
			}
		}

		/**
		 * 转换source对象字段为新的Object,大写
		 *
		 * @param source
		 * @return
		 */
		private Object convertObject(Object source) {
			if (source instanceof java.lang.Exception) return null;
			Map<String, Object> map = new HashMap<>();
			if (source instanceof java.util.Map) {
				Map<String, Object> sourceMap = (Map<String, Object>) source;
				for (Map.Entry<String, Object> entry : sourceMap.entrySet()) {
					String fieldName = entry.getKey();
					String newFieldName = fieldName.substring(0, 1).toUpperCase() + fieldName.substring(1);
					newFieldName = newFieldName.replace("-", "").replace("_", "");
					Object value = sourceMap.get(fieldName);
					map.put(newFieldName, convert(value));
				}
			} else {
				if (source.getClass().getAnnotation(IgnoreConvert.class) != null) return source;
				switch (source.getClass().getTypeName()) {
					case "byte":
						return source;
					case "short":
						return source;
					case "int":
						return source;
					case "long":
						return source;
					case "float":
						return source;
					case "double":
						return source;
					case "char":
						return source;
					case "boolean":
						return source;
					case "java.lang.String":
						return source;
					case "java.lang.Byte":
						return source;
					case "java.lang.Short":
						return source;
					case "java.lang.Integer":
						return source;
					case "java.lang.Long":
						return source;
					case "java.lang.Double":
						return source;
					case "java.lang.Float":
						return source;
					case "java.lang.Character":
						return source;
					case "java.lang.Boolean":
						return source;
					default:
						Field[] fields = source.getClass().getDeclaredFields();
						for (Field field : fields) {
							String fieldName = field.getName();
							String newFieldName = fieldName.substring(0, 1).toUpperCase() + fieldName.substring(1);
							String getter = "get" + newFieldName;
							try {
								Method method = source.getClass().getMethod(getter, new Class[]{});
								Object value = method.invoke(source, new Object[]{});
								map.put(newFieldName, convert(value));
							} catch (Exception e) {
								e.printStackTrace();
							}
						}
						break;
				}
			}
			return map;
		}
	}
}
