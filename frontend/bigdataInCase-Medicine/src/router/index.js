import Vue from 'vue'
import Router from 'vue-router'
import home from '@/components/home/config'
import disease from '@/components/disease/config'
import drug from '@/components/drug/config'

Vue.use(Router)

/**
 * $route.params,$route.query,$route.hash
 */
var router = new Router({
    // mode: 'history',
    base: '/log/',
    routes: [{
            path: '/',
            redirect: '/home'
        },
        {
            path: '/main',
            name: 'Main',
            redirect: '/home',
            component: resolve => require(['@/components/Main'], resolve),
            children: [
                home.router,
                disease.router,
                drug.router
            ]
        }
    ]
})
export default router