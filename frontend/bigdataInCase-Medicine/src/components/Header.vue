<template>
  <header class="case-head">
    	<div class="logo"><img src="../assets/img/logo.png"></div>
    	<nav class="menu">
    		<ul>
    			<li><router-link to="/home" active-class="on">首页</router-link></li>
    			<li><router-link to="/disease" active-class="on">适应症分析</router-link></li>
    			<li><router-link to="/drug" active-class="on">药品分析</router-link></li>
    		</ul>
    	</nav>
    </header>
</template>
<script>
export default {
  data() {
    return {
      courseName: ""
    };
  },
  methods: {

  }
};
</script>

