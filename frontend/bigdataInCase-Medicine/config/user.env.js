import Vue from 'vue';

let config = Vue.config;

config.testMode = false; //是否使用mock模式
config.mockServer = "http://192.168.0.80:8080/static/"; // 发起ajax请求的路径前缀
config.apiPrefix = "http://172.17.36.16:8840"; // 发起ajax请求的路径前缀
config.authApiPrefix = "http://172.17.36.16:8836";
config.timeout = 180000; // ajax的默认超时时间(ms)
config.servicetimeout = 1 * 60 * 1000; //页面重加载间隔
config.systemId = 20;
config.uploadSystemId = 22; //上报系统id
export default config;