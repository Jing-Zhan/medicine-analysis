<template>
    <div>
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
import citylevel from  '@/components/home/charts/citylevel'
import age from  '@/components/home/charts/age'
import drugTop from  '@/components/home/charts/drugTop'
import province from  '@/components/home/charts/province'
export default {
  components: {
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
