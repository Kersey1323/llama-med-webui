<template>
  <div class="container">

    <NavBar/>
    <!-- 左上角标题 -->
<!--    <div class="header">-->
<!--      <h1>智能影像学检错助手 v1.0</h1>-->
<!--    </div>-->

    <!-- 图片显示区域 -->
    <div class="image-container">
      <img class="image" src="../assets/img/img_1.png" alt="Image 1" />
      <img class="image" src="../assets/img/img_2.png" alt="Image 2" />
    </div>

    <!-- 输入框区域 -->
    <div class="input-container">
      <!-- 左侧文本框 -->
      <div class="input-box">
        <textarea v-model="inputText" placeholder="请输入文本" rows="10"></textarea>
      </div>

      <!-- 右侧参数显示框 -->
      <div class="output-box">
<!--        <textarea readonly rows="10"></textarea>-->
        <span v-html="outputText"></span>
      </div>
    </div>

    <!-- 处理按钮 -->
    <button @click="processText">开始校正</button>
  </div>
</template>

<script>
import axios from 'axios';
import NavBar from '../components/NavBar.vue';
export default {

  name: 'CorrectorPage',
  components: {
    NavBar
  },
  data() {

    return {
      inputText: '',  // 输入框文本内容
      outputText: '', // 输出框文本内容
    };
  },
  methods: {
    async processText() {
      const input_text = this.inputText;  // 获取输入框内容

      try {
        // 向后端发送请求，获取校正后的文本
        const response = await axios.post('http://localhost:8000/correct_text', {text: input_text});
        console.log(response)
        // 更新输出文本框内容
        this.outputText = this.formatReport(response.data.corrected_text);

      } catch (error) {
        console.error('Error fetching corrected text:', error);
        this.outputText = 'Error occurred while processing text';
      }
    },
       // 格式化生成的报告，将引号内的内容标记为红色
    formatReport(text) {
      console.log('Original Text:', text); // 检查原始文本
      const regex = /"([^"]+)"/g; // 匹配双引号内的内容

    const formattedText = text.replace(regex, (match, p1) => {
      console.log('Matched:', p1); // 输出匹配到的内容
      return `<span style="color: red; font-weight: bold" >${p1}</span>`;
    });
    console.log('Formatted Text:', formattedText); // 检查格式化后的文本
    return formattedText;

  },

  },
};
</script>

<style scoped>
/* 容器样式 */


/* 标题样式 */
.header {
  text-align: left;
  margin-bottom: 20px;
}

/* 图片显示区域样式 */
.image-container {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

.image {
  max-width: 20vw; /* 限制最大宽度为屏幕宽度的20% */
  height: auto; /* 保持图片高度按比例缩放 */
  display: block; /* 去掉图片底部的间隙 */
}

/* 输入框区域样式 */
.input-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-top: 20px;
}

/* 左侧文本框样式 */
.input-box textarea {
  padding: 10px;
  width: 20vw; /* 设置文本框宽度为屏幕宽度的20% */
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  resize: vertical; /* 允许调整高度 */
}

/* 右侧参数显示框样式 */
.output-box textarea {
  padding: 10px;
  width: 20vw; /* 设置文本框宽度为屏幕宽度的20% */
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f9f9f9;
  resize: vertical; /* 允许调整高度 */
  overflow-y: auto; /* 允许垂直滚动 */
}

/* 按钮样式 */
button {
  margin-top: 20px;
  padding: 10px 20px;
  font-size: 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style>
