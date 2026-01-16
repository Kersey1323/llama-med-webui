<template>
  <div class="register-container">
    <div class="register-box">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="form.username"
            required
            minlength="3"
            maxlength="20"
            placeholder="请输入用户名（3-20个字符）"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            type="email"
            id="email"
            v-model="form.email"
            required
            placeholder="请输入邮箱地址"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            required
            minlength="12"
            placeholder="请输入密码（至少12位，含大写、小写、数字、特殊字符）"
          />
          <ul class="password-rules">
            <li>密码长度至少12位</li>
            <li>必须包含大写字母、小写字母、数字和特殊字符</li>
            <li>不能为常见弱密码</li>
          </ul>
        </div>
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            type="password"
            id="confirmPassword"
            v-model="form.confirmPassword"
            required
            placeholder="请再次输入密码"
          />
        </div>
        <div class="form-group captcha-group">
          <label for="captcha">验证码</label>
          <div class="captcha-row">
            <input
              type="text"
              id="captcha"
              v-model="form.captcha"
              required
              placeholder="请输入验证码"
              maxlength="6"
              style="width: 120px; margin-right: 10px;"
            />
            <img :src="captchaImg" @click="refreshCaptcha" alt="验证码" class="captcha-img" />
          </div>
        </div>
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        <ul v-if="errorDetails.length" class="error-details">
          <li v-for="(err, idx) in errorDetails" :key="idx" class="error-detail">{{ err }}</li>
        </ul>
        <div class="form-actions">
          <button type="submit" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
          <router-link to="/login" class="login-link">
            已有账号？立即登录
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from '../utils/axios';

export default {
  name: 'Register',
  setup() {
    const router = useRouter();
    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      captcha: ''
    });
    const captchaImg = ref('');
    const captchaUuid = ref('');
    const loading = ref(false);
    const errorMsg = ref('');
    const errorDetails = ref([]);

    const refreshCaptcha = async () => {
      try {
        const res = await axios.get('/api/auth/captcha');
        captchaImg.value = res.data.img;
        captchaUuid.value = res.data.uuid;
      } catch (e) {
        captchaImg.value = '';
        captchaUuid.value = '';
      }
    };

    onMounted(refreshCaptcha);

    const validateForm = () => {
      if (form.value.password !== form.value.confirmPassword) {
        errorMsg.value = '两次输入的密码不一致';
        errorDetails.value = [];
        return false;
      }
      if (form.value.username.length < 3 || form.value.username.length > 20) {
        errorMsg.value = '用户名长度必须在3-20个字符之间';
        errorDetails.value = [];
        return false;
      }
      if (form.value.password.length < 12) {
        errorMsg.value = '密码长度至少12位';
        errorDetails.value = [];
        return false;
      }
      // 邮箱格式
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(form.value.email)) {
        errorMsg.value = '请输入有效的邮箱地址';
        errorDetails.value = [];
        return false;
      }
      if (!form.value.captcha) {
        errorMsg.value = '请输入验证码';
        errorDetails.value = [];
        return false;
      }
      errorMsg.value = '';
      errorDetails.value = [];
      return true;
    };

    const handleRegister = async () => {
      if (!validateForm()) return;
      try {
        loading.value = true;
        errorMsg.value = '';
        errorDetails.value = [];
        const { confirmPassword, ...registerData } = form.value;
        registerData.captcha_uuid = captchaUuid.value;
        const response = await axios.post('/api/auth/register', registerData);
        if (response.data.success) {
          alert('注册成功，请登录');
          router.push('/login');
        } else {
          errorMsg.value = response.data.error || response.data.message || '注册失败，请稍后重试';
          errorDetails.value = response.data.details || [];
          refreshCaptcha();
        }
      } catch (error) {
        errorMsg.value = error.response?.data?.error || error.response?.data?.message || '注册失败，请稍后重试';
        errorDetails.value = error.response?.data?.details || [];
        refreshCaptcha();
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      loading,
      handleRegister,
      captchaImg,
      refreshCaptcha,
      errorMsg,
      errorDetails
    };
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #4a90e2;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #357abd;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.form-actions {
  margin-top: 1.5rem;
}

.login-link {
  display: block;
  text-align: center;
  margin-top: 1rem;
  color: #4a90e2;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}

.password-rules {
  color: #888;
  font-size: 12px;
  margin: 4px 0 0 0;
  padding-left: 18px;
}
.captcha-group {
  margin-bottom: 1rem;
}
.captcha-row {
  display: flex;
  align-items: center;
}
.captcha-img {
  height: 36px;
  cursor: pointer;
  border: 1px solid #eee;
  border-radius: 4px;
}
.error-msg {
  color: #d32f2f;
  margin-bottom: 8px;
  font-size: 14px;
}
.error-details {
  color: #d32f2f;
  font-size: 13px;
  margin-bottom: 8px;
  padding-left: 18px;
}
.error-detail {
  margin-bottom: 2px;
}
</style> 