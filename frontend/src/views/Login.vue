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
    <h2 style="text-align:center; padding-top:50px;">Voice Chat Login</h2>
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="Username"
          label="Username"
          placeholder="Username"
          :rules="[{ required: true, message: 'Required' }]"
        />
        <van-field
          v-model="password"
          type="password"
          name="Password"
          label="Password"
          placeholder="Password"
          :rules="[{ required: true, message: 'Required' }]"
        />
      </van-cell-group>
      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit">
          Login
        </van-button>
      </div>
    </van-form>
  </div>
</template>
