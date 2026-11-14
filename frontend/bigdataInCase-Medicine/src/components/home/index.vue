<template>
    <div class="page">
        <div class="page-head">
            <div class="page-head-main">
                <h1 class="page-title">首页概览</h1>
                <p class="page-sub">整体用药规模与分布：城市等级、年龄结构、药品销额与省份格局</p>
            </div>
            <div class="page-head-side">
                <span class="chip">数据范围 <b>200812</b></span>
                <span class="chip">处方明细 <b>100 万行</b></span>
            </div>
        </div>

        <overview></overview>
        <div class="main clearfix">
            <citylevel></citylevel>
            <div class="main-right">
                <age></age>
                <drugtop></drugtop>
            </div>
        </div>
        <province></province>
    </div>
</template>
<script>
import Vue from 'vue'
import overview from  '@/components/home/charts/overview'
import citylevel from  '@/components/home/charts/citylevel'
import age from  '@/components/home/charts/age'
import drugTop from  '@/components/home/charts/drugTop'
import province from  '@/components/home/charts/province'
export default {
  components: {
    overview: overview,
    'citylevel': citylevel,
    age:age,
    'drugtop':drugTop,
    province:province
  },
  data() {
    return {
    }
  }
}
</script>
<style scoped>
.main-left{
    width: calc(50% - 10px);
    float: left;
    height: 586px;
}
.main-right{
    width: calc(50% - 10px);
    float: right;
}
.age{
    height: 292px;
}
.drug-top{
    height: 274px;
}
@media (max-width: 1440px) {
    .main-left{
        height: 436px;
    }
    .age{
        height: 217px;
    }
    .drug-top{
        height: 199px;
    }
}
</style>
