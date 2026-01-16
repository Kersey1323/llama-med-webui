<template>
  <div class="login-container">
    <div class="login-box">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="form.username"
            required
            placeholder="请输入用户名"
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            required
            placeholder="请输入密码"
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
        <div class="form-actions">
          <button type="submit" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <router-link to="/register" class="register-link">
            没有账号？立即注册
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
  name: 'Login',
  setup() {
    const router = useRouter();
    const form = ref({
      username: '',
      password: '',
      captcha: ''
    });
    const captchaImg = ref('');
    const captchaUuid = ref('');
    const loading = ref(false);
    const errorMsg = ref('');

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

    const handleLogin = async () => {
      try {
        loading.value = true;
        errorMsg.value = '';
        const loginData = {
          username: form.value.username,
          password: form.value.password,
          captcha: form.value.captcha,
          captcha_uuid: captchaUuid.value
        };
        const response = await axios.post('/api/auth/login', loginData);
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('user_id', response.data.user.id);
        localStorage.setItem('username', response.data.user.username)
        router.push('/batch-process');
      } catch (error) {
        errorMsg.value = error.response?.data?.error || error.response?.data?.message || '登录失败，请检查用户名、密码和验证码';
        refreshCaptcha();
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      loading,
      handleLogin,
      captchaImg,
      refreshCaptcha,
      errorMsg
    };
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
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

.register-link {
  display: block;
  text-align: center;
  margin-top: 1rem;
  color: #4a90e2;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
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
</style> 