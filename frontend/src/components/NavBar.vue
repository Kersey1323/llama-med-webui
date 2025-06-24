<!-- src/components/NavBar.vue -->
<template>
  <div class="container">
     <div class="top-bar">
          <el-icon :size="22" ><Switch /></el-icon>
          <el-link type="info" @click="goToCorrector">Corrector</el-link>
          <el-link type="info" @click="goToMedLLM"><span style="width: 150px">CDU-MedLM</span></el-link>
          <el-link type="info" @click="goTOBatchProgress"><span style="width: 150px">Batch-Process</span></el-link>

            <img src="../assets/logo.png" alt="Logo" class="top-bar-logo" />
     </div>
  </div>
</template>



import axios from 'axios';
import {Delete, Edit, Plus, Search, Share, Upload} from '@element-plus/icons-vue'
<script>
export default {

  methods:{
      goToMedLLM() {
         this.$router.push('/medllm');
       },

      goToCorrector() {
         this.$router.push('/corrector');
       },
    goTOBatchProgress(){
      this.$router.push('/batch-process')
    },

  }
}
</script>


<style scoped>
.top-bar {
  background-color: rgb(255, 255, 255); /* 浅灰色背景 */
  padding: 8px 5%; /* 上下8px，左右5%内边距 */
  display: flex;
  align-items: center; /* 垂直居中 */
  justify-content: flex-start; /* 左对齐 */
}

.nav-links {
  display: flex;
  gap: 20px; /* 文字之间的间距 */
}

.el-link {
  font-size: 18px;
  font-weight: 600; /* 半粗字体 */
  font-family: 'Open Sans', 'Noto Sans', sans-serif; /* 现代简洁字体 */
  color: rgb(93, 93, 93); /* 深灰色文字 */
  padding-left: 15px;
  padding-right: 15px;
  white-space: nowrap; /* 防止文字换行 */
}

.el-link span {
  display: inline-block;
  max-width: 150px; /* 限制最大宽度 */
  text-overflow: ellipsis; /* 超出文字用省略号显示 */
  overflow: hidden; /* 隐藏超出部分 */
}

.top-bar-logo {
  height: 60px; /* 调整 logo 高度 */
  width: auto;  /* 自动宽度保持比例 */
  margin-left: auto; /* 右对齐 logo */
}

.top-bar .el-link:hover {
  color: #4CAF50; /* 悬停时颜色变化 */
}

.top-bar .el-link .el-icon--right.el-icon {
  vertical-align: text-bottom;
}
</style>