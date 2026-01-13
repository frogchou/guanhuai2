<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const personas = ref([]);
const auth = useAuthStore();
const router = useRouter();

const fetchPersonas = async () => {
  try {
    const res = await axios.get('/api/v1/personas/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    personas.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

onMounted(fetchPersonas);
</script>

<template>
  <van-nav-bar title="Contacts" right-text="Add" @click-right="router.push('/personas/new')" />
  
  <van-list>
    <van-cell 
      v-for="p in personas" 
      :key="p.id" 
      :title="p.name" 
      :label="p.relationship" 
      is-link 
      :to="`/chat/${p.id}`"
    >
      <template #icon>
        <div style="margin-right: 10px; width: 40px; height: 40px; background: #ddd; border-radius: 50%; display:flex; align-items:center; justify-content:center;">
          {{ p.name[0] }}
        </div>
      </template>
    </van-cell>
  </van-list>
</template>
