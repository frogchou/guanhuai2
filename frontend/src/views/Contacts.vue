<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const personas = ref<any[]>([]);
const auth = useAuthStore();
const router = useRouter();

const fetchPersonas = async () => {
  try {
    const res = await axios.get('/api/v1/personas/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    // Sort alphabetically might be nice, but simple list for now
    personas.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

const goToAdd = () => {
  router.push('/personas/new');
};

const goToChat = (id: number) => {
  router.push(`/chat/${id}`);
};

onMounted(fetchPersonas);
</script>

<template>
  <div class="page-container">
    <van-nav-bar 
      title="Contacts" 
      class="wechat-nav"
      :border="false"
    >
      <template #right>
        <van-icon name="plus" size="18" color="#000" @click="goToAdd" />
      </template>
    </van-nav-bar>
    
    <div class="contact-list">
      <!-- New Friends Mock -->
      <div class="contact-item functional-item">
        <div class="avatar orange"><van-icon name="friends" /></div>
        <div class="name">New Friends</div>
      </div>
      
      <div class="group-title" v-if="personas.length > 0">Friends</div>
      
      <div 
        v-for="p in personas" 
        :key="p.id" 
        class="contact-item"
        @click="goToChat(p.id)"
      >
        <div class="avatar">
          {{ p.name[0] }}
        </div>
        <div class="info">
          <div class="name">{{ p.name }}</div>
        </div>
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

.contact-list {
  background-color: #fff;
}

.group-title {
  background-color: #ededed;
  color: #999;
  font-size: 12px;
  padding: 8px 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.contact-item:active {
  background-color: #d9d9d9;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  background-color: #2ba245;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  margin-right: 12px;
}

.avatar.orange {
  background-color: #fa9d3b;
}

.info {
  flex: 1;
}

.name {
  font-size: 16px;
  color: #191919;
}

.functional-item {
  margin-bottom: 0;
}
</style>