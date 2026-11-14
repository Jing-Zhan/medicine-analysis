<template>
    <div class="page">
        <div class="page-head">
            <div class="page-head-main">
                <h1 class="page-title">药品分析</h1>
                <p class="page-sub">按药品查看覆盖城市与医院、对应适应症、科室分布，以及科室用药结构对比</p>
            </div>
            <div class="page-head-side">
                <div class="case-seach">
                    <input type="text" v-model="keyword" placeholder="请输入药品名称，例如 阿司匹林">
                    <a href="javascript:;" @click="seach"><img src="../../assets/img/seach.png" alt=""></a>
                </div>
            </div>
        </div>

        <div class="main">
            <div class="main-top clearfix">
                <cities ref='cities' :keyword="keyword"></cities>
                <disease ref='disease' :keyword="keyword"></disease>
            </div>
            <div class="main-down clearfix">
                <hospital ref='hospital' :keyword="keyword"></hospital>
                <department ref='department' :keyword="keyword"></department>
            </div>
            <profile ref='profile' mode="drug"></profile>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import department from  '@/components/drug/charts/department'
import disease from  '@/components/drug/charts/disease'
import cities from  '@/components/drug/charts/cities'
import hospital from  '@/components/drug/charts/hospital'
import profile from  '@/components/common/profile'
export default {
  components: {
    'department': department,
    disease,cities,hospital,
    profile:profile
  },
  data() {
    return {
      keyword:undefined,
    }
  },
  mounted: function() {
    },
  methods: {
    seach:function(){
        this.$refs.department.getSeries();
        this.$refs.disease.getSeries();
        this.$refs.cities.getSeries();
        this.$refs.hospital.getSeries();
        this.$refs.profile.load();
      }
  }
}
</script>
<style scoped>
.city{
    width: 64%;
    float: left;
    height: 660px;
}
.diseases{
    width: calc(36% - 20px);
    float: right;
    height: 660px;
}
.hospital{
    width: calc(50% - 10px);
    float: left;
    height: 350px;
}
.section{
    width: calc(50% - 10px);
    float: right;
    height: 350px;
}
@media (max-width: 1440px) {
  .city,.diseases{
    height: 460px;
  }
  .section,.hospital{
    height: 300px;
  }
}
</style>
