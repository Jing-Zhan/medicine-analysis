/**
 * 接口适配层（假数据 / 真实接口的切换点）
 * ============================================================
 * 项目里所有图表都通过 Vue.ajax.send({ url, data, success }) 取数。
 * 这里在启动时给 Vue.ajax.send 套一层：
 *
 *   config.useMock === true  （当前阶段：接口未通）
 *       不发请求，直接从 src/mock 里取假数据交给 success，图表照样渲染。
 *   config.useMock === false （接口通了以后）
 *       正常发请求；请求失败或 8 秒没响应时回退假数据，保证页面不空白。
 *
 * 这样做的好处：组件里的取数代码一行都不用改，部署时只改 src/config.js。
 */
import Vue from 'vue'
import config from '@/config'
import mock from '@/mock'

// 请求超时后回退假数据的时间（毫秒）
const FALLBACK_TIMEOUT = 8000

// 原始 send（走 vue-http-rexsheng 的真实实现）
let nativeSend = null

/**
 * 从完整 url 里拆出接口路径和 keyword 参数
 * '/drug/cities?keyword=人参' => { path: '/drug/cities', keyword: '人参' }
 */
export function parseUrl(url) {
    var index = url.indexOf('?')
    if (index === -1) {
        return { path: url, keyword: '' }
    }
    var path = url.slice(0, index)
    var query = url.slice(index + 1)
    var keyword = ''
    query.split('&').forEach(function (item) {
        var pair = item.split('=')
        if (pair[0] === 'keyword') {
            keyword = decodeURIComponent(pair[1] || '')
        }
    })
    return { path: path, keyword: keyword }
}

/**
 * 按接口路径取假数据
 */
export function mockResponse(path, keyword) {
    var factory = mock[path]
    if (typeof factory !== 'function') {
        return { code: '200', data: [] }
    }
    return factory(keyword)
}

/**
 * 给 Vue.ajax.send 套上假数据适配层，在 Vue.use(http) 之后调用
 */
export function installMockAdapter() {
    if (!Vue.ajax || typeof Vue.ajax.send !== 'function') {
        return
    }
    nativeSend = Vue.ajax.send

    Vue.ajax.send = function (options) {
        options = options || {}
        var url = options.url || ''
        var parsed = parseUrl(url)
        var settled = false
        var timer = null

        var done = function (res) {
            if (settled) return
            settled = true
            if (timer) clearTimeout(timer)
            // 放到下一个事件循环，避免在组件 mounted 过程中同步改数据
            setTimeout(function () {
                if (typeof options.success === 'function') {
                    options.success(res)
                }
            }, config.mockDelay)
        }

        var fallback = function () {
            done(mockResponse(parsed.path, parsed.keyword))
        }

        if (config.useMock) {
            fallback()
            return
        }

        timer = setTimeout(fallback, FALLBACK_TIMEOUT)
        nativeSend.call(Vue.ajax, {
            url: url,
            data: options.data || {},
            success: function (data) {
                if (data && data.code == '200') {
                    done(data)
                } else {
                    fallback()
                }
            },
            error: fallback
        })
    }
}
