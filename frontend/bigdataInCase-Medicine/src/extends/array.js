import Vue from 'vue';

/**
 * 从对象数组中根据对象属性查找
 */

/**
 * 用于根据Key值查询的迭代器
 * 判断逻辑：对象&&有指定属性&&属性完全匹配指定值
 */
function iter (key, val) {
    return function (item) {
        if (typeof item !== 'object') return false;

        if (typeof key === 'object') {
            for (var k in key) {
                if (Vue.getData(item, k) !== key[k]) {
                    return false;
                }
            }
            return true;
        } else {
            var ori = Vue.getData(item, key);
            if (typeof val === 'undefined') {
                return !!ori;
            } else {
                return typeof ori !== 'undefined' && ori === val;
            }
        }
    };
}

var propotype = {
    /**
     * 根据对象属性查找数组中第一个符合条件的对象
     */
    findProperty (key, val) {
        return this.find(iter.apply(this, arguments));
    },
    /**
     * 过滤出所有符合对象属性的数据
     */
    filterProperty (key, val) {
        return this.filter(iter.apply(this, arguments));
    },
    /**
     * 判断是否所有对象属性都存在并不是false
     */
    everyProperty (key, val) {
        return this.every(iter.apply(this, arguments));
    },
    /**
     * 判断是否至少有一条对象属性存在并不是false
     */
    someProperty (key, val) {
        return this.some(iter.apply(this, arguments));
    },
    /**
     * 根据对象属性排序（正序，如果需要倒序，需要再使用reverse）
     */
    sortProperty (key) {
        return this.sort(function (x, y) {
            return x[key] > y[key];
        });
    },
    /**
     * 返回对象数组的字段映射值
     * 两种实现：
     *    1: 传入字符串   [{A:2},{A:3},{A:true}].mapProperty('A')  => [2,3,true]
     *    2: 传入字段映射 [{A:3,B:{C:4}},{A:4,B:{C:6}},{A:5,B:{C:8}}].mapProperty({'B.C':'d'})
     *        => [{d:4},{d:6},{d:8}]
     */
    mapProperty (prop) {
        return this.map(function (next) {
            if (typeof prop === 'object') {
                var rst = {};
                Object.keys(prop).forEach(k => {
                    Vue.setData(rst, prop[k], Vue.getData(next, k));
                });
                return rst;
            } else {
                return Vue.getData(next, prop);
            }
        });
    },
    /**
     * 数组去重（按值比较）
     */
    distinct () {
        return Array.from(new Set(this));
    },
    /**
     * 在原有数组上追加新数组
     * 区别于concat
     */
    pushObjects (arr) {
        var _self = this;
        arr.forEach((item) => {
            _self.push(item);
        });
        return this;
    },
    /**
     * 给数组对象中的每一个对象的某个属性都赋值
     */
    setEach (key, value) {
        return this.forEach(function (item) {
            Vue.setData(item, key, value);
        });
    },
    /**
     * 二维数组合并为一维数组
     */
    merges () {
        var result = [];
        this.forEach((item) => {
            result = result.concat(item);
        });
        return result;
    },
    /**
     * 二维数组合并为一维数组
     */
    assign () {
        var arr = new Array();
        this.forEach((item) => {
            var tem = Object.assign({},item);
            arr.push(tem);
        });
        return arr;
    },
    /**
     * 添加新元素（唯一性）
     */
    pushUnique (obj) {
        if (!this.includes(obj)) {
            this.push(obj);
        }
        return this;
    },
    removeAt (index) {
        return this.splice(index, 1);
    },
    /**
     * 从数组中去除指定对象
     * @param {Object} obj
     */
    removeObject (obj) {
        var index = this.indexOf(obj);
        while (index >= 0) {
            this.splice(index, 1);
            index = this.indexOf(obj);
        }
        return this;
    },
    insertAt (index, obj) {
        var right = this.splice(index);
        this.push(obj);
        this.pushObjects(right);
        return this;
    },
    /**
     * 返回排除掉指定值后的数组
     */
    without (value) {
        if (!this.includes(value)) return this;
        var ret = [];
        this.forEach(k => {
            if (k !== value) ret.push(k);
        });
        return ret;
    },
    // es6 使用set去重
    uniq () {
        return this.distinct();
    },
    /**
       Sort an array by the key specified in the argument.
      Handle only native js objects as element of array, not the Ember's object.

      Can be used as alternative to sortProperty method of Ember library
      in order to speed up executing on large data volumes

      @method sortBy
      @param {String} path name(s) to sort on
      @return {Array} The sorted array.
      */
    sortPropertyLight (path) {
        var realPath = (typeof path === 'string') ? path.split('.') : [];
        this.sort(function (a, b) {
            var aProperty = a;
            var bProperty = b;
            realPath.forEach(function (key) {
                aProperty = aProperty[key];
                bProperty = bProperty[key];
            });
            if (aProperty > bProperty) return 1;
            if (aProperty < bProperty) return -1;
            return 0;
        });
        return this;
    },
    /**
     * Create wick map from array
     * Example:
     * <pre>
     *   var array = [{a: 1}, {a: 2}, {a: 3}];
     *   var map = array.toWickMapByProperty('a'); // {1: true, 2: true, 3: true}
     * </pre>
     * <code>map[1]</code> works faster than <code>array.someProperty('a', 1)</code>
     *
     * @param {string} property
     * @return {object}
     * @method toWickMapByProperty
     * @see toMapByCallback
     */
    toWickMapByProperty (property) {
        return this.toMapByCallback(property, function () {
            return true;
        });
    },
    /**
     * Create map from array with executing provided callback for each array's item
     * Example:
     * <pre>
     *   var array = [{a: 1, b: 3}, {a: 2, b: 2}, {a: 3, b: 1}];
     *   var map = array.toMapByCallback('a', function (item) {
     *    return Em.get(item, 'b');
     *   });
     *   console.log(map); // {1: 3, 2: 2, 3: 1}
     * </pre>
     * <code>map[1]</code> is much more faster than <code>array.findProperty('a', 1).get('b')</code>
     *
     * @param {string} property
     * @param {Function} callback
     * @returns {object}
     * @method toMapByCallback
     */
    toMapByCallback (property, callback) {
        var ret = {};
        this.forEach(function (item) {
            var key = Vue.getData(item, property);
            ret[key] = callback(item, property);
        });
        return ret;
    },
    reject (callback, target) {
        return this.filter(function () {
            return !(callback.apply(target, arguments));
        });
    },
    /**
     * 从列表中根据属性排除数据
     */
    rejectProperty (key, value) {
        var exactValue = function (item) { return Vue.getData(item, key) === value; };
        var hasValue = function (item) { return !!Vue.getData(item, key); };
        var use = (arguments.length === 2 ? exactValue : hasValue);
        return this.reject(use);
    },
    toWickMap () {
        var ret = {};
        this.forEach(function (item) {
            ret[item] = true;
        });
        return ret;
    },
    /**
     * Create map from array
     * Example:
     * <pre>
     *   var array = [{a: 1}, {a: 2}, {a: 3}];
     *   var map = array.toMapByProperty('a'); // {1: {a: 1}, 2: {a: 2}, 3: {a: 3}}
     * </pre>
     * <code>map[1]</code> is much more faster than <code>array.findProperty('a', 1)</code>
     *
     * @param {string} property
     * @return {object}
     * @method toMapByProperty
     * @see toMapByCallback
     */
    toMapByProperty (property) {
        return this.toMapByCallback(property, function (item) {
            return item;
        });
    },
    /**
     * 获取数组最后一条
     *
     * @returns obj
     */
    lastObject () {
        var len = this.length;
        if (len === 0) return undefined;
        var last = this[this.length - 1];
        return last;
    },
    /** @private - more optimized version */
    firstObject () {
        var len = this.length;
        if (len === 0) return undefined;
        var first = this[0];
        return first;
    }
};
Object.assign(Array.prototype, propotype);
