import Vue from 'vue'
Vue.prototype.$setInterval = function(cb, timeMilliseconds) {
    var _this = this;
    let intervalHandler = setInterval(function() {
        if (_this && !_this._isDestroyed) {
            cb();
        } else {
            clearInterval(intervalHandler);
            return;
        }
    }, timeMilliseconds);
    return intervalHandler;
}

Vue.prototype.$setTimeout = function(cb, timeMilliseconds) {
    var _this = this;
    let intervalHandler = setTimeout(function() {
        if (_this && !_this._isDestroyed) {
            cb();
        } else {
            clearTimeout(intervalHandler);
            return;
        }
    }, timeMilliseconds);
    return intervalHandler;
}