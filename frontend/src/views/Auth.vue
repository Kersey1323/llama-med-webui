<template>
  <div class="auth-container">
<!--    <img src="@/assets/logo.png" alt="logo" class="logo-img-fixed"/>-->
    <div class="login-card">
      <p class="title">{{ mode === 'login' ? '登录到CDU-RD' : '注册 CDU-RD' }}</p>
      <div class="input-card">
        <el-form :model="mode === 'login' ? loginForm : registerForm" class="login-form">
          <template v-if="mode === 'login'">
            <el-form-item>
              <el-input
                  v-model="loginForm.identifier"
                  placeholder="输入用户名或邮箱"
              >
                <template #prefix>
                  <el-icon>
                    <User/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                  v-model="loginForm.password"
                  placeholder="输入您的密码"
                  show-password
              >
                <template #prefix>
                  <el-icon>
                    <Lock/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item v-if="loginForm.captcha !== undefined">
              <el-input
                  v-model="loginForm.captcha"
                  placeholder="验证码"
                  maxlength="6"
                  style="width: 60%"
              >
                <template #prefix>
                  <el-icon>
                    <Key/>
                  </el-icon>
                </template>
              </el-input>
              <img :src="captchaImg" @click="refreshCaptcha" class="captcha-img" alt="验证码"
                   style="height: 40px; margin-left: 10px; border-radius: 6px; border: 1px solid #eee; background: #fafafa; cursor: pointer;"/>
            </el-form-item>
          </template>
          <template v-else>
            <el-form-item>
              <el-input
                  v-model="registerForm.email"
                  placeholder="输入您的电子邮箱"
              >
                <template #prefix>
                  <el-icon>
                    <Message/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                  v-model="registerForm.username"
                  placeholder="输入您的名称"
              >
                <template #prefix>
                  <el-icon>
                    <User/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                  v-model="registerForm.password"
                  placeholder="输入您的密码"
                  show-password
              >
                <template #prefix>
                  <el-icon>
                    <Lock/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                  v-model="registerForm.confirmPassword"
                  placeholder="再次输入您的密码"
                  show-password
              >
                <template #prefix>
                  <el-icon>
                    <Lock/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-input
                  v-model="registerForm.captcha"
                  placeholder="验证码"
                  maxlength="6"
                  style="width: 60%"
              >
                <template #prefix>
                  <el-icon>
                    <Key/>
                  </el-icon>
                </template>
              </el-input>
              <img :src="captchaImg" @click="refreshCaptcha" class="captcha-img" alt="验证码"
                   style="height: 40px; margin-left: 10px; border-radius: 6px; border: 1px solid #eee; background: #fafafa; cursor: pointer;"/>
            </el-form-item>
            <div class="password-rules">
              <ul>
                <li>密码长度至少12位</li>
                <li>必须包含大写字母、小写字母、数字和特殊字符</li>
                <li>不能为常见弱密码</li>
              </ul>
            </div>
            <div v-if="registerErrorMsg" class="error-msg">{{ registerErrorMsg }}</div>
            <ul v-if="registerErrorDetails.length" class="error-details">
              <li v-for="(err, idx) in registerErrorDetails" :key="idx" class="error-detail">{{ err }}</li>
            </ul>
          </template>
        </el-form>
      </div>
      <div v-if="mode === 'login'">
        <div class="forgot-password"><a href="#">忘记密码</a></div>
        <el-button type="primary" class="login-button" @click="handleLogin" plain block
                   :disabled="!canLogin || loginLoading">
          {{ loginLoading ? '登录中...' : '登录' }}
        </el-button>
        <div class="register">
          没有账号？
          <a href="#" @click.prevent="mode = 'register'">注册</a>
        </div>
      </div>
      <div v-else>
        <el-button type="primary" class="login-button" @click="handleRegister" plain block
                   :disabled="!canRegister || registerLoading">
          {{ registerLoading ? '注册中...' : '创建账号' }}
        </el-button>
        <div class="register">
          已经拥有账号？
          <a href="#" @click.prevent="mode = 'login'">登录</a>
        </div>
      </div>
    </div>
    <div class="footer">您的登录即表示接受 <a href="#">用户条款</a> 和 <a href="#">隐私协议</a></div>
  </div>
</template>

<script>
import {ref, computed} from 'vue';
import {useRouter} from 'vue-router';
import axios from '../utils/axios';
import {User, Lock, Key, Message} from '@element-plus/icons-vue';
import {ElMessage, ElMessageBox} from "element-plus";

export default {
  name: 'Auth',
  components: {User, Lock, Key, Message},
  data() {
    return {
      mode: 'login',
      loginForm: {
        identifier: '',
        password: '',
        captcha: '',
      },
      registerForm: {
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        captcha: '',
      },
      captchaImg: '',
      captchaUuid: '',
      loginLoading: false,
      registerLoading: false,
      loginErrorMsg: '',
      registerErrorMsg: '',
      registerErrorDetails: [],
    };
  },
  computed: {
    canLogin() {
      return (
          this.loginForm.identifier &&
          this.loginForm.password &&
          this.loginForm.captcha
      );
    },
    canRegister() {
      return (
          this.registerForm.email &&
          this.registerForm.username &&
          this.registerForm.password &&
          this.registerForm.confirmPassword &&
          this.registerForm.captcha
      );
    },
  },
  mounted() {
    this.refreshCaptcha();
  },
  methods: {
    async refreshCaptcha() {
      try {
        const res = await axios.get('/api/auth/captcha');
        this.captchaImg = res.data.img;
        this.captchaUuid = res.data.uuid;
      } catch (e) {
        this.captchaImg = '';
        this.captchaUuid = '';
      }
    },
    async handleLogin() {
      if (!this.canLogin || this.loginLoading) return;
      this.loginLoading = true;
      this.loginErrorMsg = '';
      try {
        const loginData = {
          username: this.loginForm.identifier,
          password: this.loginForm.password,
          captcha: this.loginForm.captcha,
          captcha_uuid: this.captchaUuid
        };
        const response = await axios.post('/api/auth/login', loginData);
        console.log('登录成功，后端返回：', response);
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user_id', response.data.user.id);
        localStorage.setItem('username', response.data.user.username);
        this.$router.push('/batch-process');
      } catch (error) {
        console.error('登录失败，后端返回：', error.response);
        this.loginErrorMsg = error.response?.data?.error || error.response?.data?.message || '登录失败，请检查用户名/邮箱、密码和验证码';
        ElMessage(this.loginErrorMsg);
        this.refreshCaptcha();
      } finally {
        this.loginLoading = false;
      }
    },
    async handleRegister() {
      if (!this.canRegister || this.registerLoading) return;
      // 前端简单校验
      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.registerErrorMsg = '两次输入的密码不一致';
        this.registerErrorDetails = [];
        return;
      }
      this.registerLoading = true;
      this.registerErrorMsg = '';
      this.registerErrorDetails = [];
      try {
        const {confirmPassword, ...registerData} = this.registerForm;
        registerData.captcha_uuid = this.captchaUuid;
        const response = await axios.post('/api/auth/register', registerData);
        console.log(response)
        if (response.status === 201) {
          this.registerErrorMsg = '';
          this.registerErrorDetails = [];
          this.mode = 'login';
          await this.$nextTick(() => {
            this.loginErrorMsg = '注册成功，请登录';
            // console.log(this.loginErrorMsg)
            // ElMessageBox(this.loginErrorMsg)
            // this.$router.push('/auth')
          });
          this.registerForm.password = '';
          this.registerForm.confirmPassword = '';
          this.registerForm.captcha = '';
          this.refreshCaptcha();
        } else {
          this.registerErrorMsg = response.data.error || response.data.message || '注册失败，请稍后重试';
          this.registerErrorDetails = response.data.details || [];
          this.refreshCaptcha();
        }
      } catch (error) {
        this.registerErrorMsg = error.response?.data?.error || error.response?.data?.message || '注册失败，请稍后重试';
        this.registerErrorDetails = error.response?.data?.details || [];
        this.refreshCaptcha();
      } finally {
        this.registerLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.auth-container {
  background-image: url('/assets/Background.jpg');
  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  //background: #f9f9f9;
  font-family: "Helvetica Neue", sans-serif;
}

.logo-img-fixed {
  position: absolute;
  top: 32px;
  left: 32px;
  height: 100px;
  z-index: 10;
}

.login-card {
  width: 420px;
  background: #fff;
  padding: 48px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.10);
  border-radius: 16px;
  position: relative;
}

.input-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  padding: 0;
  margin-bottom: 32px;
  overflow: hidden;
}

.login-form {
  width: 100%;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 0;
}

.login-form :deep(.el-form-item:not(:last-child)) {
  border-bottom: 1px solid #f0f0f0;
}

.login-form :deep(.el-input__wrapper) {
  border: none !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 12px 16px 12px 18px !important;
  min-height: 20px !important;
  font-size: 17px !important;
}

.login-form :deep(.el-input__inner) {
  font-size: 17px !important;
  line-height: 1.6;
  padding: 0 !important;
}

.login-form :deep(.el-form-item:first-child .el-input__wrapper) {
  border-top-left-radius: 12px !important;
  border-top-right-radius: 12px !important;
}

.login-form :deep(.el-form-item:last-child .el-input__wrapper) {
  border-bottom-left-radius: 12px !important;
  border-bottom-right-radius: 12px !important;
}

:deep(.el-input__prefix .el-icon) {
  color: #5cb6ff !important;
}

.title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 32px;
  font-weight: 500;
  font-family: "PingFang SC";
}

.forgot-password {
  text-align: right;
  margin: 18px 0 24px 0;
}

.forgot-password a {
  font-size: 13px;
  color: #409EFF;
}

.login-button {
  width: 100%;
  margin: 0 0 18px 0;
  border-radius: 14px;
  height: 48px;
  font-size: 18px;
}

.login-button[disabled] {
  background: #eee !important;
  color: #bbb !important;
  border-color: #eee !important;
  cursor: not-allowed !important;
}

.register {
  text-align: center;
  font-size: 13px;
  margin-bottom: 12px;
}

.register a {
  color: #409EFF;
  margin-left: 4px;
}

.divider {
  display: none;
}

.oauth-button {
  display: none;
}

.password-rules {
  color: #888;
  font-size: 12px;
  margin: 4px 0 0 0;
  padding-left: 18px;
}

.footer {
  margin-top: 20px;
  font-size: 12px;
  color: #999;
}

.footer a {
  color: #409EFF;
}

.error-msg {
  color: #f56c6c;
  font-size: 12px;
  margin-bottom: 12px;
}

.error-details {
  list-style-type: none;
  padding-left: 0;
}

.error-detail {
  color: #f56c6c;
  font-size: 12px;
  margin-bottom: 4px;
}
</style>
