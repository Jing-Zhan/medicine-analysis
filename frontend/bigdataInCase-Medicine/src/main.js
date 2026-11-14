import Vue from 'vue'
import echarts from 'echarts/lib/echarts'
import App from './app'
import router from './router'
import './extends/index'
import config from '@/config'
import http from 'vue-http-rexsheng'
import { installMockAdapter } from '@/api'
import './assets/css/css.css'
import './assets/css/theme.css'
import medTheme from './echarts-theme'

// 图表统一登记一份主题，坐标轴、网格、图例与提示框在各页面保持一致
echarts.registerTheme('med', medTheme)

Vue.use(http)

// 接口地址 / mock 开关统一由 src/config.js 控制，部署时只改那一个文件
Vue.config.testMode = http.ajax.config.mockMode = false;
Vue.config.apiPrefix = http.ajax.config.baseUrl = config.baseUrl;
Vue.config.baseUrl = config.baseUrl;
Vue.config.useMock = config.useMock;
http.ajax.config.default = {
    timeout: 30000,
    type: "get"
}

// 接口未通时用前端假数据渲染（开关在 src/config.js 的 useMock）
installMockAdapter()

/**
 * 系统入口
 */
new Vue({
    el: '#app',
    router,
    template: '<App/>',
    components: { App },
    beforeCreate: function() {
        if (window.console && PRODUCT_ENV) {
            window.console.log("已禁用console调试！");
            window.console.log = function() {};
            window.console.warn = function() {};
            window.console.error = function() {};
            window.console.info = function() {};
            window.console.debug = function() {};
            window.console.assert = function() {};
            window.console.trace = function() {};
        }
    }
})
