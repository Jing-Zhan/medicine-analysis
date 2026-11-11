<template>
        <div class="main clearfix">
          <div class="case-seach">
            <input type="text" v-model="keyword" placeholder="请输入目标适应症">
            <a href="javascript:;" @click="seach"><img src="../../assets/img/seach.png" alt=""></a>
          </div>
            <div class="main-left">
                <group ref='group' :keyword="keyword"></group>
                <union ref='union' :keyword="keyword"></union>
                <department ref='department' :keyword="keyword"></department>
            </div>            
            <age ref='age' :keyword="keyword"></age>
        </div>   
</template>
<script>
import Vue from 'vue'
import age from  '@/components/disease/charts/age'
import department from  '@/components/disease/charts/department'
import group from  '@/components/disease/charts/group'
import union from  '@/components/disease/charts/union'
export default {
  components: {
    'age': age,
    department:department,
    union:union,
    group:group
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
