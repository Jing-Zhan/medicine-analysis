import Vue from 'vue'
import App from './App'
import router from './router'
import './extends/index'
import '@/config';
import http from 'vue-http-rexsheng'
import basic from './assets/css/css.css'
Vue.use(http)

require.context("./assets/data/", true, /\.json$/);

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