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
const avatarFile = ref([]);
const auth = useAuthStore();
const router = useRouter();

const onClickLeft = () => {
  router.push('/contacts');
};

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

    // 3. Upload Avatar if exists
    if (avatarFile.value.length > 0) {
      const formData = new FormData();
      formData.append('file', avatarFile.value[0].file);
      await axios.post(`/api/v1/personas/${personaId}/avatar`, formData, {
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
  <div class="page-container">
    <van-nav-bar 
      title="Add Contact" 
      left-arrow 
      @click-left="onClickLeft" 
      class="wechat-nav"
      :border="false"
    />
    
    <van-form @submit="onSubmit" class="create-form">
      <div class="form-group-title">Avatar</div>
      <div class="avatar-uploader-container">
         <van-uploader v-model="avatarFile" max-count="1" preview-size="80px" />
      </div>

      <div class="form-group-title">Basic Info</div>
      <van-cell-group :border="false" class="wechat-cell-group">

        <van-field 
          v-model="form.name" 
          name="Name" 
          label="Name" 
          placeholder="e.g. Grandma" 
          :rules="[{ required: true }]" 
          input-align="right"
        />
        <van-field 
          v-model="form.relationship" 
          name="Relation" 
          label="Relation" 
          placeholder="e.g. Grandmother" 
          input-align="right"
        />
      </van-cell-group>

      <div class="form-group-title">Interaction Settings</div>
      <van-cell-group :border="false" class="wechat-cell-group">
        <van-field 
          v-model="form.persona_called_by" 
          name="CalledBy" 
          label="Calls you" 
          placeholder="e.g. Sweetie" 
          input-align="right"
        />
        <van-field 
          v-model="form.user_called_by" 
          name="CallsUser" 
          label="You call her" 
          placeholder="e.g. Grandma" 
          input-align="right"
        />
      </van-cell-group>
      
      <div class="form-group-title">Voice Clone</div>
      <van-cell-group :border="false" class="wechat-cell-group">
        <van-field name="uploader" label="Voice Sample" input-align="right">
          <template #input>
            <van-uploader 
              v-model="voiceFile" 
              max-count="1" 
              accept="audio/*" 
              result-type="file"
              :preview-image="false"
            >
              <van-button icon="music-o" size="small" type="default">Select Audio</van-button>
            </van-uploader>
          </template>
        </van-field>
      </van-cell-group>
      
      <div style="padding: 20px 16px;">
        <van-checkbox v-model="form.legal_confirmed" shape="square" icon-size="16px">
          <span style="font-size: 13px; color: #666;">I confirm I have the legal rights to clone this voice.</span>
        </van-checkbox>
      </div>

      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" class="wechat-btn">
          Complete
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #ededed;
}

.wechat-nav {
  background-color: #ededed;
  --van-nav-bar-title-text-color: #000;
  --van-nav-bar-title-font-weight: 600;
  --van-nav-bar-icon-color: #000;
}

.form-group-title {
  padding: 16px 16px 8px;
  font-size: 14px;
  color: #888;
}

.wechat-cell-group {
  margin: 0;
  border-radius: 0;
}

.create-form {
  padding-bottom: 30px;
}

.wechat-btn {
  background-color: #07c160;
  border-color: #07c160;
  height: 48px;
  font-size: 17px;
  font-weight: 500;
}

.avatar-uploader-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
  background-color: #fff;
}
</style>
