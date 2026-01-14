<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const active = ref(0);
const router = useRouter();
</script>

<template>
  <div class="app-layout">
    <div class="content">
      <router-view />
    </div>
    
    <van-tabbar v-model="active" route safe-area-inset-bottom>
      <van-tabbar-item replace to="/chats" icon="chat-o">微信</van-tabbar-item>
      <van-tabbar-item replace to="/contacts" icon="friends-o">通讯录</van-tabbar-item>
      <van-tabbar-item replace to="/me" icon="user-o">我</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #ededed;
}

.content {
  flex: 1;
  overflow-y: auto;
  /* Padding for tabbar */
  padding-bottom: 50px; 
}

:deep(.van-tabbar) {
  background-color: #f7f7f7;
  border-top: 1px solid #e5e5e5;
}

:deep(.van-tabbar-item--active) {
  color: #07c160;
  background-color: #f7f7f7;
}
</style>
