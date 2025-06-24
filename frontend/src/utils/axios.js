import axios from 'axios';

// 创建 axios 实例
const instance = axios.create({
  // 使用相对路径，通过Vite代理转发到后端
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 对文件上传请求特殊处理
    if (config.data instanceof FormData) {
      // 文件上传使用更长的超时时间
      config.timeout = 60000;
      // 删除Content-Type，让浏览器自动设置为multipart/form-data
      delete config.headers['Content-Type'];
    }
    
    // 确保每次请求都带上X-Requested-With头
    config.headers['X-Requested-With'] = 'XMLHttpRequest';

    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  response => response,
  error => {
    // 只对非登录/注册接口的 401 做跳转
    const isAuthApi = error.config && error.config.url && (
      error.config.url.includes('/api/auth/login') ||
      error.config.url.includes('/api/auth/register')
    );
    if (error.response && error.response.status === 401 && !isAuthApi) {
      localStorage.removeItem('token');
      window.location.href = '/auth'; // 或 '/login'，看你的路由
    }
    return Promise.reject(error);
  }
);
export default instance; 