<template>
  <header class="case-head">
    <div class="brand">
      <span class="brand-mark">医</span>
      <span class="brand-name">目标适应症及用药数据分析</span>
      <span class="brand-tag">v1.0</span>
    </div>
    <nav class="menu">
      <ul>
        <li><router-link to="/home" active-class="on">首页</router-link></li>
        <li><router-link to="/disease" active-class="on">适应症分析</router-link></li>
        <li><router-link to="/drug" active-class="on">药品分析</router-link></li>
      </ul>
    </nav>
    <div class="head-meta">
      <span class="dot"></span>
      <span>数据取自后端接口</span>
    </div>
  </header>
</template>
<script>
export default {
  data() {
    return {};
  }
};
</script>
