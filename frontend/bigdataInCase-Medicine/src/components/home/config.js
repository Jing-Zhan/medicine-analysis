import config from "../../config";
import http from 'vue-http-rexsheng'
export default {
    router: {
        path: "/home",
        component: {
            template: '<router-view></router-view>'
        },
        children: [{
                path: "",
                component: resolve => require(['@/components/home/index'], resolve)
            },
        ]
    }
}
//引入mockjs
const Mock = require("mockjs");
//使用mockjs模拟数据
var Random = Mock.Random
http.ajax.addMock("logdemo/viewlist/pvuv",()=>{
    return {
        code: 200,
        msg: "查询成功",
        result:{	
            pvList:[100,200,300,400,500,600],
            uvList:[100,200,300,400,500,600]		
        }
    }
});
http.ajax.addMock("logdemo/viewlist/return",()=>{
    return {
        code: 200,
        msg: "查询成功",
        result:['154(50.78%)',200,300,400,500]
    }
});
http.ajax.addMock("logdemo/viewlist/traffic",()=>{
    return {
        code: 200,
        msg: "查询成功",
        'result':[[[7220, 3900, 9001, 10134, 10290, 2030],[12220, 9182, 8191, 7234, 6290, 4330,]],[[10220, 13900, 5001, 4134, 6290, 8030, 11010],[6220, 4182, 9191, 2234, 9290, 14330, 10010]],
        [[5220, 6900, 8001, 1134, 1290, 6030, 2010],[2220, 6182, 3191, 5234, 8290, 10330, 13010]]]
    }
});
http.ajax.addMock("logdemo/viewlist/evilIp",(index)=>{
    var rlt={
        code: 200,
        msg: "查询成功",
        result:[]
    }
    for(var i=0;i<6;i++){
        rlt.result.push({
            ip: '192.168.1.'+i,
            'num': Math.random()*10, 
            rate: '20%'
        })
    }
    return rlt;
});
http.ajax.addMock("logdemo/viewlist/serverVisit",(param)=>{
    return {
        code: 200,
        msg: "查询成功",
        result:[
            {value:33435, name:'服务器1'},
            {value:34410, name:'服务器2'},
            {value:24434, name:'服务器3'},
            {value:11235, name:'服务器4'}
        ]
    }
});
// Mock.mock("/mock/traffic/list", {
//     code: 200,
// 	msg: "查询成功",
//     'result|1':[[[7220, 3900, 9001, 10134, 10290, 2030],[12220, 9182, 8191, 7234, 6290, 4330,]],[[10220, 13900, 5001, 4134, 6290, 8030, 11010],[6220, 4182, 9191, 2234, 9290, 14330, 10010]],
//     [[5220, 6900, 8001, 1134, 1290, 6030, 2010],[2220, 6182, 3191, 5234, 8290, 10330, 13010]]]
// });
// Mock.mock("/mock/ip/list", {
//     code: 200,
// 	msg: "查询成功",
//     'result|6':[{
//         ip: '192.168.1.45',
//         'num|1-200': 2, 
//         rate: '20%'
//     }]
// });