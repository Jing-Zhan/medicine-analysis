import Vue from 'vue'
import http from 'vue-http-rexsheng'
let config = Vue.config;

config.testMode=http.ajax.config.mockMode = false; //是否使用mock模式
config.apiPrefix=http.ajax.config.baseUrl = "http://192.168.8.63:83"; // 发起ajax请求的路径前缀
http.ajax.config.default={
    timeout:30000,
    type:"get"
}
export default config;