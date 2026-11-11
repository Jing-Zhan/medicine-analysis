<template>
  <div class="hello">
    <topheader></topheader>
    <router-view></router-view>
  </div>
</template>

<script>
import Header from "@/components/Header";
export default {
  components: {
    topheader: Header
  },
  data() {
    return {
      msg: "Welcome to Your Vue.js App"
    };
  }
};
</script>

