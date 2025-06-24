<template>
  <el-container class="medllm-page">
    <!-- 左侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo-container">
        <div class="logo"></div>
        <span class="logo-text">CDU-MED</span>
      </div>
      <el-menu
        default-active="chat"
        class="el-menu-vertical-demo"
        @select="handleMenuSelect"
      >
        <el-menu-item index="chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>对话模式</span>
        </el-menu-item>
        <el-menu-item index="batch-process">
          <el-icon><Files /></el-icon>
          <span>批量处理</span>
        </el-menu-item>
      </el-menu>

      <!-- 用户信息 -->
      <div class="user-info">
        <el-dropdown trigger="click" @command="handleUserCommand">
          <div class="dropdown-trigger">
            <el-avatar :size="30" class="user-avatar">K</el-avatar>
            <span class="username">{{ username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 上部模型选择 -->
      <el-header height="60px" class="main-header">
        <el-select v-model="selectedModel" placeholder="选择模型" class="model-select">
          <el-option label="Report-Model" value="report-model" />
        </el-select>
      </el-header>

      <!-- 中间内容区 -->
      <el-container>
        <!-- 左侧历史记录 -->
        <el-aside width="240px" class="history-aside">
          <!-- 新建对话按钮 -->
          <el-button class="new-chat-button" type="primary" @click="startNewChat">
            <el-icon><Plus /></el-icon>
            新建对话
          </el-button>

          <!-- 搜索框 -->
          <div class="search-box">
            <el-input
              v-model="searchQuery"
              placeholder="搜索历史对话"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <!-- 历史对话列表 -->
          <div class="history-list-container">
            <div class="history-title">全部对话</div>
            <div class="history-list">
              <div 
                v-for="(item, index) in filteredHistory" 
                :key="index" 
                class="history-item"
                @click="selectHistory(item)"
              >
                <div class="history-item-title">{{ item.title }}</div>
                <div class="history-item-date">上次对话: {{ item.date }}</div>
              </div>
            </div>
          </div>
        </el-aside>

        <!-- 右侧聊天区域 -->
        <el-main class="chat-main">
          <!-- 聊天消息区域 -->
          <div class="chat-messages" ref="chatBox">
            <div 
              v-for="(message, index) in messages" 
              :key="index" 
              :class="['message', message.from]"
            >
              <div class="message-avatar">
                <el-avatar v-if="message.from === 'bot'" :size="36" class="bot-avatar">C</el-avatar>
                <el-avatar v-else :size="36" class="user-avatar">K</el-avatar>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="message.text"></div>
                <div class="message-actions" v-if="message.from === 'bot'">
                  <el-button type="text" @click="copyMessage(message)">
                    <el-icon><DocumentCopy /></el-icon>
                  </el-button>
                  <el-button type="text" @click="likeMessage(message)">
                    <el-icon><Sunny /></el-icon>
                  </el-button>
                  <el-button type="text" @click="dislikeMessage(message)">
                    <el-icon><Moon /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="input-tabs">
              <el-radio-group v-model="currentInput" size="small">
                <el-radio-button label="desc">影像描述</el-radio-button>
                <el-radio-button label="report">影像诊断</el-radio-button>
              </el-radio-group>
            </div>

            <div class="input-container">
              <el-input
                v-if="currentInput === 'desc'"
                v-model="imageDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入影像描述"
                resize="none"
              />
              <el-input
                v-else
                v-model="trueReport"
                type="textarea"
                :rows="3"
                placeholder="请输入影像诊断"
                resize="none"
              />
              
              <div class="submit-area">
                <el-button
                  type="primary"
                  :disabled="!canSubmit"
                  @click="submitForm"
                  circle
                >
                  <el-icon><Position /></el-icon>
                </el-button>
              </div>
            </div>
            
            <div class="input-footer">
              <span class="input-tip">请在影像描述和影像诊断中分别输入相关信息</span>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import {
  ChatDotRound,
  Files,
  Plus,
  Search,
  DocumentCopy,
  Sunny,
  Moon,
  Position,
  ArrowDown
} from '@element-plus/icons-vue';

const router = useRouter();
const chatBox = ref(null);
const imageDescription = ref('');
const trueReport = ref('');
const currentInput = ref('desc');
const selectedModel = ref('report-model');
const searchQuery = ref('');
const username = ref(localStorage.getItem('username') || 'Kersey1323');

// 模拟历史对话数据
const historyData = ref([
  { id: 1, title: '双肺数枚结节，主要结节位于左上肺尖', date: '2024-01-20' },
  { id: 2, title: '隐源术后改变：左侧颈、顶周部', date: '2024-01-19' },
]);

// 过滤历史数据
const filteredHistory = computed(() => {
  if (!searchQuery.value) return historyData.value;
  return historyData.value.filter(item => 
    item.title.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// 消息列表
const messages = ref([
  { from: 'bot', text: '你好！我是报告生成助手，很高兴为您服务。我可以帮助您生成影像报告，请问有什么我可以帮您的吗？' }
]);

// 判断是否可以提交
const canSubmit = computed(() => {
  return imageDescription.value.trim() && trueReport.value.trim();
});

// 菜单选择处理
const handleMenuSelect = (index) => {
  if (index === 'batch-process') {
    router.push('/batch-process');
  }
};

// 用户下拉菜单处理
const handleUserCommand = (command) => {
  if (command === 'logout') {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    ElMessage.success('退出登录成功');
    router.push('/login');
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能待实现');
  }
};

// 开始新对话
const startNewChat = () => {
  messages.value = [
    { from: 'bot', text: '你好！我是报告生成助手，很高兴为您服务。我可以帮助您生成影像报告，请问有什么我可以帮您的吗？' }
  ];
  imageDescription.value = '';
  trueReport.value = '';
  scrollToBottom();
};

// 选择历史对话
const selectHistory = (item) => {
  ElMessage.info(`选择了对话: ${item.title}`);
  // 这里应该从服务器获取历史对话内容
};

// 复制消息
const copyMessage = (message) => {
  const plainText = message.text.replace(/<[^>]*>?/gm, '');
  navigator.clipboard.writeText(plainText)
    .then(() => ElMessage.success('复制成功'))
    .catch(() => ElMessage.error('复制失败'));
};

// 点赞/踩消息
const likeMessage = () => ElMessage.success('感谢您的反馈！');
const dislikeMessage = () => ElMessage.info('感谢您的反馈，我们会继续改进');

// 格式化生成的报告，将引号内的内容标记为红色
const formatReport = (text) => {
  const regex = /"([^"]+)"/g; // 匹配双引号内的内容
  return text.replace(regex, (match, p1) => {
    return `<span style="color: red; font-weight: bold">${p1}</span>`;
  });
};

// 打字机效果
const typeWriter = (text) => {
  let i = 0;
  const interval = setInterval(() => {
    if (i < text.length) {
      messages.value[messages.value.length - 1].text += text.charAt(i);
      i++;
      scrollToBottom();
    } else {
      clearInterval(interval);
    }
  }, 20);
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatBox.value) {
      chatBox.value.scrollTop = chatBox.value.scrollHeight;
    }
  });
};

// 提交表单
const submitForm = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请同时输入影像描述和影像诊断');
    return;
  }
  
  messages.value.push({
    from: 'user', 
    text: `影像描述: ${imageDescription.value}\n影像诊断: ${trueReport.value}`
  });
  
  messages.value.push({ from: 'bot', text: '正在生成诊断报告...' });
  scrollToBottom();
  
  try {
    const response = await axios.post('/process', {
      desc: imageDescription.value,
      true_report: trueReport.value
    });
    
    const generatedReport = response.data.generated_report;
    messages.value.pop(); // 移除"正在生成..."消息
    messages.value.push({ from: 'bot', text: '' });
    
    // 使用打字机效果显示格式化后的报告
    typeWriter(formatReport(generatedReport));
    
    // 清空输入
    imageDescription.value = '';
    trueReport.value = '';
  } catch (error) {
    console.error("Error during request:", error);
    messages.value.pop();
    messages.value.push({ from: 'bot', text: '生成报告时发生错误，请稍后再试。' });
  }
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
/* 总体页面布局 */
.medllm-page {
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.logo-container {
  display: flex;
  align-items: center;
  padding: 20px;
}

.logo {
  height: 36px;
  width: 36px;
  margin-right: 10px;
  border-radius: 50%;
  background-color: #8e44ad;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: #8e44ad;
}

.el-menu {
  border-right: none;
  flex-grow: 1;
}

.el-menu-item.is-active {
  background-color: #8e44ad !important;
  color: #fff !important;
}

.user-info {
  padding: 16px;
  border-top: 1px solid #e6e6e6;
  margin-top: auto;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  margin-right: auto;
}

/* 主容器 */
.main-container {
  flex-direction: column;
  height: 100%;
}

.main-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.model-select {
  width: 180px;
}

/* 历史记录侧边栏 */
.history-aside {
  background-color: #f9f9f9;
  border-right: 1px solid #e6e6e6;
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.new-chat-button {
  margin-bottom: 16px;
  background-color: #8e44ad;
  border-color: #8e44ad;
  color: #fff;
}

.new-chat-button:hover,
.new-chat-button:focus {
  background-color: #7d32a8;
  border-color: #7d32a8;
}

.search-box {
  margin-bottom: 16px;
}

.history-list-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-title {
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e6e6e6;
}

.history-list {
  overflow-y: auto;
  flex-grow: 1;
}

.history-item {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  background-color: #fff;
  border: 1px solid #e6e6e6;
}

.history-item:hover {
  background-color: #f0f0f0;
}

.history-item-title {
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item-date {
  font-size: 12px;
  color: #666;
}

/* 聊天主区域 */
.chat-main {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message-avatar {
  margin-right: 12px;
}

.bot-avatar {
  background-color: #8e44ad;
  color: #fff;
}

.user-avatar {
  background-color: #409eff;
  color: #fff;
}

.message-content {
  max-width: 80%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 8px;
  white-space: pre-line;
  line-height: 1.6;
}

.message.user {
  justify-content: flex-end;
}

.message.user .message-content {
  order: 1;
}

.message.user .message-avatar {
  order: 2;
  margin-right: 0;
  margin-left: 12px;
}

.message.user .message-text {
  background-color: #ecf5ff;
  color: #333;
}

.message.bot .message-text {
  background-color: #f5f7fa;
  color: #333;
}

.message-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
}

/* 输入区域 */
.input-area {
  border-top: 1px solid #e6e6e6;
  padding: 16px;
  background-color: #fff;
}

.input-tabs {
  margin-bottom: 12px;
}

.input-container {
  position: relative;
  margin-bottom: 8px;
}

.submit-area {
  position: absolute;
  right: 8px;
  bottom: 8px;
}

:deep(.el-button--primary) {
  background-color: #8e44ad;
  border-color: #8e44ad;
}

:deep(.el-button--primary:hover),
:deep(.el-button--primary:focus) {
  background-color: #7d32a8;
  border-color: #7d32a8;
}

.input-footer {
  display: flex;
  justify-content: space-between;
}

.input-tip {
  font-size: 12px;
  color: #999;
}

:deep(.el-textarea__inner) {
  min-height: 80px !important;
  padding-right: 45px;
}

:deep(.el-radio-button__inner) {
  background-color: #f5f7fa;
}

:deep(.el-radio-button__original) {
  opacity: 0;
}

:deep(.el-radio-button__inner) {
  padding: 8px 16px;
}
</style>
