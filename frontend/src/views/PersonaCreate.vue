<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const form = ref({
  name: '',
  relationship: '',
  user_called_by: '',
  persona_called_by: '',
  legal_confirmed: false
});

const voiceFile = ref([]);
const auth = useAuthStore();
const router = useRouter();

const onSubmit = async () => {
  if (!form.value.legal_confirmed) {
    showToast('Please confirm legal rights');
    return;
  }
  
  try {
    // 1. Create Persona
    const res = await axios.post('/api/v1/personas/', form.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    const personaId = res.data.id;
    
    // 2. Upload Voice if exists
    if (voiceFile.value.length > 0) {
      const formData = new FormData();
      formData.append('file', voiceFile.value[0].file);
      await axios.post(`/api/v1/personas/${personaId}/voice`, formData, {
        headers: { 
          Authorization: `Bearer ${auth.token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
    }
    
    showToast('Created successfully');
    router.push('/');
  } catch (e) {
    showToast('Failed to create');
  }
};
</script>

<template>
  <van-nav-bar title="New Contact" left-arrow @click-left="router.back()" />
  
  <van-form @submit="onSubmit">
    <van-cell-group inset>
      <van-field v-model="form.name" name="Name" label="Name" placeholder="Grandma" rules="[{ required: true }]" />
      <van-field v-model="form.relationship" name="Relation" label="Relation" placeholder="Grandmother" />
      <van-field v-model="form.persona_called_by" name="CalledBy" label="She calls you" placeholder="Sweetie" />
      <van-field v-model="form.user_called_by" name="CallsUser" label="You call her" placeholder="Grandma" />
      
      <van-field name="uploader" label="Voice Sample">
        <template #input>
          <van-uploader v-model="voiceFile" max-count="1" accept="audio/*" />
        </template>
      </van-field>
      
      <van-field name="checkbox" label="Legal">
        <template #input>
          <van-checkbox v-model="form.legal_confirmed" shape="square">
            I confirm I have the rights to clone this voice.
          </van-checkbox>
        </template>
      </van-field>
    </van-cell-group>
    <div style="margin: 16px;">
      <van-button round block type="primary" native-type="submit">
        Create & Train
      </van-button>
    </div>
  </van-form>
</template>
