<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const username = ref('');
const password = ref('');
const auth = useAuthStore();
const router = useRouter();

const onSubmit = async () => {
  try {
    await auth.login(username.value, password.value);
    showToast('Login Success');
    router.push('/');
  } catch (e) {
    showToast('Login Failed');
  }
};
</script>

<template>
  <div class="login-page">
    <div class="top-spacer"></div>
    <h2 class="title">Log In</h2>
    
    <van-form @submit="onSubmit" class="login-form">
      <div class="input-group">
        <div class="input-label">Account</div>
        <input 
          v-model="username" 
          class="wechat-input" 
          placeholder="Mobile number / ID"
        />
      </div>
      
      <div class="input-group">
        <div class="input-label">Password</div>
        <input 
          v-model="password" 
          type="password" 
          class="wechat-input" 
          placeholder="Password"
        />
      </div>
      
      <div class="submit-area">
        <van-button 
          block 
          type="primary" 
          native-type="submit" 
          class="wechat-btn"
          :disabled="!username || !password"
        >
          Log In
        </van-button>
      </div>
    </van-form>
    
    <div class="bottom-links">
      <span>Unable to Log In?</span>
      <span class="divider">|</span>
      <span>More Options</span>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  background-color: #fff;
  padding: 0 32px;
  display: flex;
  flex-direction: column;
}

.top-spacer {
  height: 100px;
}

.title {
  font-size: 22px;
  color: #191919;
  margin-bottom: 60px;
  font-weight: 500;
}

.login-form {
  flex: 1;
}

.input-group {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding: 16px 0;
  margin-bottom: 10px;
}

.input-label {
  width: 80px;
  font-size: 16px;
  color: #191919;
}

.wechat-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: #191919;
}

.wechat-input::placeholder {
  color: #b2b2b2;
}

.submit-area {
  margin-top: 40px;
}

.wechat-btn {
  background-color: #07c160;
  border-color: #07c160;
  border-radius: 8px;
  font-size: 17px;
  font-weight: 500;
  height: 48px;
}

.wechat-btn[disabled] {
  background-color: #e0e0e0;
  border-color: #e0e0e0;
  color: #b2b2b2;
  opacity: 1;
}

.bottom-links {
  padding-bottom: 40px;
  text-align: center;
  font-size: 14px;
  color: #576b95;
  display: flex;
  justify-content: center;
}

.divider {
  margin: 0 10px;
  color: #e5e5e5;
}
</style>
