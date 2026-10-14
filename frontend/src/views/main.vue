<template>
  <router-view v-if="$route.meta.authPage || $route.meta.standalone" />
  <StudioShell v-else><router-view /></StudioShell>
</template>
<script setup>
import StudioShell from "../studio/StudioShell.vue";
</script>
