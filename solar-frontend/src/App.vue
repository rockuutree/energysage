<!-- src/App.vue -->
<template>
  <div class="app">

    <SolarMap />
  </div>
</template>

<script setup lang="ts">
import SolarMap from './components/SolarMap.vue';
</script>

<style>
body {
  margin: 0;
  padding: 0;
}

.app {
  width: 100vw;
  height: 100vh;
}
</style>