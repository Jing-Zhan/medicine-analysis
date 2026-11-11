<template>
    <div class="main">
      <div class="case-seach">
            <input type="text" v-model="keyword" placeholder="请输入药品名称">
            <a href="javascript:;" @click="seach"><img src="../../assets/img/seach.png" alt=""></a>
          </div>
        <div class="main-top clearfix">
            <cities ref='cities' :keyword="keyword"></cities>
            <disease ref='disease' :keyword="keyword"></disease>
        </div>
        <div class="main-down clearfix">
            <hospital ref='hospital' :keyword="keyword"></hospital>
            <department ref='department' :keyword="keyword"></department>
        </div>
    </div>  
</template>
<script>
import Vue from 'vue'
import department from  '@/components/drug/charts/department'
import disease from  '@/components/drug/charts/disease'
import cities from  '@/components/drug/charts/cities'
import hospital from  '@/components/drug/charts/hospital'
export default {
  components: {
    'department': department,
    disease,cities,hospital
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
