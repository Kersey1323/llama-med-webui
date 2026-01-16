<template>
  <div class="layout">
    <Navbar />
    <main class="main-content">
      <slot></slot>
    </main>
  </div>
</template>

<script>
import Navbar from './Navbar.vue'

export default {
  name: 'Layout',
  components: {
    Navbar
  }
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 50px;
}
</style> 