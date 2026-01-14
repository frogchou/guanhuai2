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
const isSubmitting = ref(false);
const isVoiceUploading = ref(false);
const voiceUploadStatus = ref<'idle' | 'uploading' | 'success' | 'error'>('idle');

const onClickLeft = () => {
  router.push('/contacts');
};

const onSubmit = async () => {
  if (isSubmitting.value || isVoiceUploading.value) {
    return;
  }
  if (!form.value.legal_confirmed) {
    showToast('请先确认您拥有合法使用该声音的权利');
    return;
  }
  isSubmitting.value = true;
  voiceUploadStatus.value = 'idle';
  try {
    const res = await axios.post('/api/v1/personas/', form.value, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    const personaId = res.data.id;
    if (voiceFile.value.length > 0) {
      isVoiceUploading.value = true;
      voiceUploadStatus.value = 'uploading';
      const formData = new FormData();
      formData.append('file', voiceFile.value[0].file);
      try {
        await axios.post(`/api/v1/personas/${personaId}/voice`, formData, {
          headers: {
            Authorization: `Bearer ${auth.token}`,
            'Content-Type': 'multipart/form-data'
          }
        });
        voiceUploadStatus.value = 'success';
      } catch (e) {
        voiceUploadStatus.value = 'error';
        throw e;
      } finally {
        isVoiceUploading.value = false;
      }
    }
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
    showToast('创建成功');
  } catch (e) {
    showToast('创建失败');
  } finally {
    isSubmitting.value = false;
    isVoiceUploading.value = false;
  }
};
</script>

<template>
  <div class="page-container">
    <van-nav-bar 
      title="添加联系人" 
      left-arrow 
      @click-left="onClickLeft" 
      class="wechat-nav"
      :border="false"
    />
    
    <van-form @submit="onSubmit" class="create-form">
      <div class="form-group-title">头像</div>
      <div class="avatar-uploader-container">
         <van-uploader v-model="avatarFile" max-count="1" preview-size="80px" />
      </div>

      <div class="form-group-title">基本信息</div>
      <van-cell-group :border="false" class="wechat-cell-group">

        <van-field 
          v-model="form.name" 
          name="Name" 
          label="姓名" 
          placeholder="例如：奶奶" 
          :rules="[{ required: true }]" 
          input-align="right"
        />
        <van-field 
          v-model="form.relationship" 
          name="Relation" 
          label="关系" 
          placeholder="例如：外婆" 
          input-align="right"
        />
      </van-cell-group>

      <div class="form-group-title">互动设置</div>
      <van-cell-group :border="false" class="wechat-cell-group">
        <van-field 
          v-model="form.persona_called_by" 
          name="CalledBy" 
          label="称呼你" 
          placeholder="例如：小宝贝" 
          input-align="right"
        />
        <van-field 
          v-model="form.user_called_by" 
          name="CallsUser" 
          label="你称呼她" 
          placeholder="例如：奶奶" 
          input-align="right"
        />
      </van-cell-group>
      
      <div class="form-group-title">声音克隆</div>
      <van-cell-group :border="false" class="wechat-cell-group">
        <van-field name="uploader" label="声音样本" input-align="right">
          <template #input>
            <van-uploader 
              v-model="voiceFile" 
              max-count="1" 
              accept="audio/*" 
              result-type="file"
              :preview-image="false"
            >
              <van-button icon="music-o" size="small" type="default">选择音频</van-button>
            </van-uploader>
          </template>
        </van-field>
        <div class="upload-status" v-if="voiceUploadStatus === 'uploading'">
          正在上传声音样本...
        </div>
        <div class="upload-status success" v-else-if="voiceUploadStatus === 'success'">
          声音样本已上传。
        </div>
        <div class="upload-status error" v-else-if="voiceUploadStatus === 'error'">
          声音上传失败，请重试。
        </div>
      </van-cell-group>
      
      <div style="padding: 20px 16px;">
        <van-checkbox v-model="form.legal_confirmed" shape="square" icon-size="16px">
          <span style="font-size: 13px; color: #666;">我确认已获得合法授权，可以克隆该声音。</span>
        </van-checkbox>
      </div>

      <div style="margin: 16px;">
        <van-button 
          round 
          block 
          type="primary" 
          native-type="submit" 
          class="wechat-btn"
          :loading="isSubmitting"
          :disabled="isSubmitting || isVoiceUploading"
        >
          完成
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
