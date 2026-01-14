<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';
import { showToast } from 'vant';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const personaId = route.params.id;

const messages = ref<any[]>([]);
const persona = ref<any | null>(null);
const isRecording = ref(false);
const mediaRecorder = ref<MediaRecorder | null>(null);
const audioChunks = ref<Blob[]>([]);
const pollingInterval = ref<any>(null);
const createdBlobUrls = new Set<string>();

const chatContainer = ref<HTMLElement | null>(null);

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
};

const fetchMessages = async () => {
  try {
    const res = await axios.get(`/api/v1/conversations/${personaId}/messages`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    // Check if new messages arrived to scroll down
    if (res.data.length > messages.value.length) {
      scrollToBottom();
    }
    messages.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

const fetchPersona = async () => {
  try {
    const res = await axios.get('/api/v1/personas/', {
      headers: { Authorization: `Bearer ${auth.token}` }
    });
    const idNum = Number(personaId);
    persona.value = res.data.find((p: any) => p.id === idNum) || null;
  } catch (e) {
    console.error(e);
  }
};

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const preferredMime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : (MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : '');
    mediaRecorder.value = preferredMime ? new MediaRecorder(stream, { mimeType: preferredMime }) : new MediaRecorder(stream);
    audioChunks.value = [];
    
    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data);
    };
    
    mediaRecorder.value.start();
    isRecording.value = true;
  } catch (e) {
    showToast('麦克风访问被拒绝');
  }
};

const stopRecording = () => {
  if (!mediaRecorder.value) return;
  
  mediaRecorder.value.onstop = async () => {
    const useWebm = mediaRecorder.value && mediaRecorder.value.mimeType && mediaRecorder.value.mimeType.includes('webm');
    const audioBlob = new Blob(audioChunks.value, { type: useWebm ? 'audio/webm' : 'audio/wav' });
    const formData = new FormData();
    formData.append('file', audioBlob, useWebm ? 'voice.webm' : 'voice.wav');
    
    // Optimistic UI: Add user message immediately
    const blobUrl = URL.createObjectURL(audioBlob);
    createdBlobUrls.add(blobUrl);
    
    messages.value.push({
      role: 'user',
      status: 'completed',
      audio_url: blobUrl
    });
    scrollToBottom();
    
    try {
      await axios.post(`/api/v1/conversations/${personaId}/send`, formData, {
        headers: { 
          Authorization: `Bearer ${auth.token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      fetchMessages(); // Refresh to get real ID and trigger backend
    } catch (e) {
      showToast('发送失败');
    }
  };
  
  mediaRecorder.value.stop();
  isRecording.value = false;
};

onMounted(() => {
  fetchPersona();
  fetchMessages();
  pollingInterval.value = setInterval(fetchMessages, 3000); // Poll every 3s
});

onUnmounted(() => {
  clearInterval(pollingInterval.value);
  createdBlobUrls.forEach(url => URL.revokeObjectURL(url));
  createdBlobUrls.clear();
});
</script>

<template>
  <div class="chat-layout">
    <van-nav-bar 
      title="聊天" 
      left-arrow 
      @click-left="router.back()" 
      fixed 
      placeholder 
      class="wechat-nav"
    >
      <template #right>
        <van-icon name="ellipsis" size="20" color="#000" />
      </template>
    </van-nav-bar>
    
    <div class="messages" ref="chatContainer">
      <div v-for="msg in messages" :key="msg.id" :class="['message-row', msg.role]">
        <div class="avatar-container" v-if="msg.role === 'assistant'">
          <div class="avatar assistant-avatar">
            <img 
              v-if="persona && persona.avatar_url" 
              :src="persona.avatar_url" 
              alt="avatar" 
            />
            <span v-else>
              {{ persona && persona.name && persona.name.length ? persona.name[0] : '助' }}
            </span>
          </div>
        </div>
        
        <div class="content-container">
          <div v-if="msg.analysis && msg.role === 'assistant'" class="meta-tag">
             情绪：{{ msg.analysis.tone }}
          </div>
          
          <div class="bubble">
            <div v-if="msg.content_text" class="text-content">{{ msg.content_text }}</div>
            
            <div v-if="msg.audio_url" class="audio-player">
              <audio controls :src="msg.audio_url" class="wechat-audio"></audio>
            </div>
            
            <div v-if="msg.status === 'processing'" class="loading-indicator">
              <van-loading type="spinner" size="16px" />
            </div>
          </div>
        </div>

        <div class="avatar-container" v-if="msg.role === 'user'">
          <div class="avatar user-avatar">我</div>
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <div class="tool-icon">
        <van-icon name="volume-o" size="28" />
      </div>
      
      <div 
        class="record-btn" 
        :class="{ active: isRecording }"
        @mousedown="startRecording" 
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
      >
        {{ isRecording ? '松开发送' : '按住说话' }}
      </div>
      
      <div class="tool-icon">
        <van-icon name="smile-o" size="28" />
      </div>
      
      <div class="tool-icon">
        <van-icon name="add-o" size="28" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #ededed;
}

.wechat-nav {
  background-color: #ededed;
  --van-nav-bar-title-text-color: #000;
  --van-nav-bar-title-font-weight: 600;
  --van-nav-bar-icon-color: #000;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #ededed;
}

.message-row {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  overflow: hidden;
}

.assistant-avatar {
  background-color: #fff;
  color: #333;
  margin-right: 10px;
}

.user-avatar {
  background-color: #2ba245; /* WeChat green */
  color: #fff;
  margin-left: 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.content-container {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.assistant .content-container {
  align-items: flex-start;
}

.user .content-container {
  align-items: flex-end;
}

.bubble {
  padding: 10px 14px;
  border-radius: 4px;
  position: relative;
  font-size: 16px;
  line-height: 1.5;
  word-wrap: break-word;
}

.assistant .bubble {
  background: white;
  border: 1px solid #e5e5e5;
}

.assistant .bubble::before {
  content: "";
  position: absolute;
  left: -6px;
  top: 14px;
  width: 10px;
  height: 10px;
  background: white;
  border-left: 1px solid #e5e5e5;
  border-bottom: 1px solid #e5e5e5;
  transform: rotate(45deg);
}

.user .bubble {
  background: #95ec69;
  border: 1px solid #8ad963;
}

.user .bubble::after {
  content: "";
  position: absolute;
  right: -6px;
  top: 14px;
  width: 10px;
  height: 10px;
  background: #95ec69;
  border-right: 1px solid #8ad963;
  border-top: 1px solid #8ad963;
  transform: rotate(45deg);
}

.text-content {
  color: #191919;
}

.wechat-audio {
  height: 30px;
  max-width: 200px;
}

.input-area {
  min-height: 56px;
  background: #f7f7f7;
  display: flex;
  align-items: center;
  border-top: 1px solid #dcdcdc;
  padding: 8px 10px;
  /* Safe area for iPhone X+ */
  padding-bottom: env(safe-area-inset-bottom);
}

.tool-icon {
  width: 40px;
  display: flex;
  justify-content: center;
  color: #191919;
}

.record-btn {
  flex: 1;
  height: 40px;
  border-radius: 4px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-size: 16px;
  color: #191919;
  user-select: none;
  cursor: pointer;
  margin: 0 10px;
  border: 1px solid #e5e5e5;
}

.record-btn.active {
  background: #dcdcdc;
  color: #555;
}

.meta-tag {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.loading-indicator {
  display: flex;
  justify-content: center;
  padding: 5px;
}
</style>
