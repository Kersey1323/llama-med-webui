import { createApp } from 'vue';
import Main from './views/main.vue'; // 使用新的主组件
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 创建 Vue 应用
const app = createApp(Main);

// 使用 ElementPlus
app.use(ElementPlus);

// 使用路由
app.use(router);

// 注册 ElementPlus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 将 ElMessage 暴露到全局，供 axios 拦截器使用
window.ElMessage = ElMessage;

// 挂载应用
app.mount('#app');