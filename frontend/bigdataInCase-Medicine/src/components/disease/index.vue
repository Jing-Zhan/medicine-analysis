<template>
    <div class="page">
        <div class="page-head">
            <div class="page-head-main">
                <h1 class="page-title">适应症分析</h1>
                <p class="page-sub">按疾病查看关联药品、联合用药、年龄与科室分布，以及费用负担</p>
            </div>
            <div class="page-head-side">
                <div class="case-seach">
                    <input type="text" v-model="keyword" placeholder="请输入目标适应症，例如 腺癌">
                    <a href="javascript:;" @click="seach"><img src="../../assets/img/seach.png" alt=""></a>
                </div>
            </div>
        </div>

        <div class="main clearfix">
            <div class="main-left">
                <group ref='group' :keyword="keyword"></group>
                <union ref='union' :keyword="keyword"></union>
                <department ref='department' :keyword="keyword"></department>
            </div>
            <age ref='age' :keyword="keyword"></age>
            <profile ref='profile' mode="disease"></profile>
        </div>
    </div>
</template>
<script>
import Vue from 'vue'
import age from  '@/components/disease/charts/age'
import department from  '@/components/disease/charts/department'
import group from  '@/components/disease/charts/group'
import union from  '@/components/disease/charts/union'
import profile from  '@/components/common/profile'
export default {
  components: {
    'age': age,
    department:department,
    union:union,
    group:group,
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
        this.$refs.group.getSeries();
        this.$refs.union.getSeries();
        this.$refs.age.getSeries();
        this.$refs.department.getSeries();
        this.$refs.profile.load();
      }
    }
}
</script>
<style scoped>
.main-left{
    width: 70%;
    float: left;
}
.main-right{
    width: calc(30% - 20px);
    height: 953px;
    float: right;
}
.group{
    width: 58%;
    height: 604px;
    float: left;
}
.union{
    width: calc(42% - 20px);
    height: 604px;
    float: right;
}
.section{
    height: 330px;
    clear: both;
}
.echarts{
  width: 100%;
  height: calc(100% - 80px);
}
@media (max-width: 1440px) {
  .group,.union{
    height: 404px;
  }
  .section{
    height: 330px;
  }
  .main-right{
    height: 753px;
  }
}
</style>
