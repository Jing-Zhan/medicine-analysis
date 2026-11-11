import Vue from 'vue';

/**
 * 对Vue对象的扩展
 * ==============================================
 */

/**
 * setter getter
 */
let _vue_ = {
    STORE_MAIN_KEY: 'templateweb',
    set store(data) {
        this._data = data;
        localStorage[this.STORE_MAIN_KEY] = JSON.stringify(data);
    },
    get store() {
        if (!this._data) {
            var storeStr = localStorage[this.STORE_MAIN_KEY];
            if (storeStr === undefined) {
                localStorage[this.STORE_MAIN_KEY] = '{}';
                this._data = {};
            } else {
                this._data = JSON.parse(storeStr);
            }
            console.log('BY-PRODUCE-WEB localStorage 数据初始化');
        }
        return this._data;
    }
};

/**
 * 获取登录用户信息
 */
Vue.getUser = function() {
    return Vue.getData('loginuser');
};

/**
 * 通过Vue对象设置数据，有两种重载
 *  给指定对象赋值 Vue.setData({},'key','val')
 *  存储到Vue全局 Vue.setData('key','val')
 * 注：第二种视情况可考虑修改为存储到localStorage
 */
Vue.setData = function() {
    var obj, key, val, lastobj, initData;
    if (arguments.length === 3) {
        obj = arguments[0];
        key = arguments[1];
        val = arguments[2];
        lastobj = obj;
    } else {
        key = arguments[0];
        val = arguments[1];
        initData = lastobj = _vue_.store;
    }
    var paths = key.split('.');
    for (var i = 0; i < paths.length - 1; i++) {
        if (Vue.isNone(lastobj[paths[i]])) {
            lastobj[paths[i]] = {};
        }
        lastobj = lastobj[paths[i]];
    }
    lastobj[paths[paths.length - 1]] = val;
    if (arguments.length === 2) _vue_.store = initData;
};

/**
 * 通过Vue获取数据，有多种重载
 * Vue.getData([obj],key,[defaultVal])
 *  获取指定对象的属性Vue.getData({},'key')
 *  获取Vue全局对象的属性Vue.getData('key')
 *  带有默认值 Vue.getData('key',[])
 * 注：obj不能是字符串，不过可以使用new String(str)
 */
Vue.getData = function() {
    var obj, key, lastobj, defaultVal;
    var args = arguments;

    if (typeof args[0] !== 'string' && typeof args[1] === 'string') {
        obj = args[0];
        lastobj = obj;
        Array.prototype.shift.call(args);
    } else {
        lastobj = _vue_.store;
    }
    key = args[0];
    defaultVal = args[1];

    var paths = key.split('.');
    for (var i = 0; i < paths.length; i++) {
        if (Vue.isNone(lastobj)) return defaultVal;
        lastobj = lastobj[paths[i]];
    }
    return lastobj === undefined ? defaultVal : lastobj;
};

/**
 * 判断对象是否为空（null和undefined）
 */
Vue.isNone = function(obj) {
    return obj === null || obj === undefined;
};

Vue.isNull = function(obj) {
    return obj === null || obj === undefined || obj === '';
};
/**
 * 清空 localStorage 数据
 */
Vue.cleanUp = function() {
    Vue.setData("loginuser", {});
    Vue.setData("token", "");
    // localStorage.removeItem(_vue_.STORE_MAIN_KEY)
};
/**
 * 是否为空数组
 */
Vue.isEmpty = function(obj) {
    return Vue.isNone(obj) || (obj.length === 0 && typeof obj !== 'function') || (typeof obj === 'object' && obj.length === 0);
};

/**
 * 判断对象是否包含属性
 */
Vue.isEmptyObject = function(obj) {
    var empty = true;
    obj = obj || {};
    for (var prop in obj) { if (obj.hasOwnProperty(prop)) { empty = false; break; } }
    return empty;
};

/**
 * 根据对象的指定字段重新生成对象
 * ({A:1,B:2,C:{D:'ok'}},['A','C.D'] => {A:1,'C.D':'ok'}
 * @param target 目标对象
 * @param propertyNames 属性名数组
 * @param inDeep 属性名是否是深度属性【false】
 */
Vue.getProperties = function(target, propertyNames, inDeep) {
    var ret = {};
    for (var i = 0; i < propertyNames.length; i++) {
        ret[propertyNames[i]] = inDeep ? Vue.getData(target, propertyNames[i]) : target[propertyNames[i]];
    }
    return ret;
};

/**
 * 批量设置对象属性
 * ({},{A:1,B:2})
 */
Vue.setProperties = function(target, properties) {
    for (var name in properties) {
        target[name] = properties[name];
    }
};

/** 验证权限是否存在 */
Vue.authorize = function(auths) {
    var arr = auths.split(',');
    var result = false;
    var authArr = Vue.getData('loginuser.authList') || [];
    result = authArr.some(auth => arr.indexOf(auth.authCode) > -1);

    return result;
};
/**
 * 根据大小写字母和数字生成随机字符串
 *
 * @param {number} len 生成的长度
 * @param {String} [allowed] 随机生成的内容的可选择内容
 */
Vue.getRandomString = function(len, allowed) {
    var text = '';
    allowed = typeof allowed === 'string' ? allowed : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < len; i++) {
        text += allowed.charAt(Math.floor(Math.random() * allowed.length));
    }
    return text;
};