<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const personas = ref<any[]>([]);
const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);

const fetchPersonas = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/api/v1/personas/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    // Mocking last message for chat list appearance
    personas.value = res.data.map((p: any) => ({
      ...p,
      lastMessage: "Click to start chatting...",
      time: "Just now"
    }));
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const goToChat = (id: number) => {
  router.push(`/chat/${id}`);
};

onMounted(fetchPersonas);
</script>

<template>
  <div class="page-container">
    <van-nav-bar title="WeChat" :border="false" class="wechat-nav" />
    
    <div v-if="loading" class="loading-state">
      <van-loading type="spinner" />
    </div>
    
    <div v-else class="chat-list">
      <div 
        v-for="p in personas" 
        :key="p.id" 
        class="chat-item"
        @click="goToChat(p.id)"
      >
        <div class="avatar">
          {{ p.name[0] }}
        </div>
        <div class="chat-info">
          <div class="chat-top">
            <span class="name">{{ p.name }}</span>
            <span class="time">{{ p.time }}</span>
          </div>
          <div class="chat-bottom">
            <span class="last-msg">{{ p.lastMessage }}</span>
          </div>
        </div>
      </div>
      
      <div v-if="personas.length === 0" class="empty-state">
        No conversations yet. Go to Contacts to add someone.
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100%;
  background-color: #ededed;
}

.wechat-nav {
  background-color: #ededed;
  --van-nav-bar-title-text-color: #000;
  --van-nav-bar-title-font-weight: 600;
}

:deep(.van-nav-bar__title) {
  font-weight: bold;
}

.chat-list {
  background-color: #fff;
}

.chat-item {
  display: flex;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.chat-item:active {
  background-color: #d9d9d9;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  background-color: #2ba245;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  margin-right: 12px;
  flex-shrink: 0;
}

.chat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.chat-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.name {
  font-size: 16px;
  color: #191919;
  font-weight: 500;
}

.time {
  font-size: 12px;
  color: #b2b2b2;
}

.chat-bottom {
  display: flex;
}

.last-msg {
  font-size: 14px;
  color: #b2b2b2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loading-state, .empty-state {
  display: flex;
  justify-content: center;
  padding-top: 50px;
  color: #999;
}
</style>