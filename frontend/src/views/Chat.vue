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
const isRecording = ref(false);
const mediaRecorder = ref<MediaRecorder | null>(null);
const audioChunks = ref<Blob[]>([]);
const pollingInterval = ref<any>(null);

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

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.value = new MediaRecorder(stream);
    audioChunks.value = [];
    
    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data);
    };
    
    mediaRecorder.value.start();
    isRecording.value = true;
  } catch (e) {
    showToast('Microphone access denied');
  }
};

const stopRecording = () => {
  if (!mediaRecorder.value) return;
  
  mediaRecorder.value.onstop = async () => {
    const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('file', audioBlob, 'voice.wav');
    
    // Optimistic UI: Add user message immediately
    messages.value.push({
      role: 'user',
      status: 'completed',
      audio_url: URL.createObjectURL(audioBlob)
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
      showToast('Failed to send');
    }
  };
  
  mediaRecorder.value.stop();
  isRecording.value = false;
};

onMounted(() => {
  fetchMessages();
  pollingInterval.value = setInterval(fetchMessages, 3000); // Poll every 3s
});

onUnmounted(() => {
  clearInterval(pollingInterval.value);
});
</script>

<template>
  <div class="chat-layout">
    <van-nav-bar title="Chat" left-arrow @click-left="router.back()" fixed placeholder />
    
    <div class="messages" ref="chatContainer">
      <div v-for="msg in messages" :key="msg.id" :class="['message-row', msg.role]">
        <div class="bubble">
          <div v-if="msg.content_text" class="text-content">{{ msg.content_text }}</div>
          
          <div v-if="msg.audio_url" class="audio-player">
            <audio controls :src="msg.audio_url"></audio>
          </div>
          
          <div v-if="msg.analysis && msg.role === 'assistant'" class="meta-tag">
             Mood: {{ msg.analysis.tone }}
          </div>
          
          <div v-if="msg.status === 'processing'" class="loading-indicator">
            Thinking...
          </div>
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <div 
        class="record-btn" 
        :class="{ active: isRecording }"
        @mousedown="startRecording" 
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
      >
        {{ isRecording ? 'Release to Send' : 'Hold to Speak' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background: #f2f2f2;
}
.message-row {
  display: flex;
  margin-bottom: 15px;
}
.message-row.user {
  justify-content: flex-end;
}
.message-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 80%;
  padding: 10px;
  border-radius: 10px;
  background: white;
}
.user .bubble {
  background: #95ec69;
}
.input-area {
  height: 80px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #ddd;
}
.record-btn {
  width: 80%;
  height: 50px;
  border-radius: 25px;
  background: #f2f2f2;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  user-select: none;
  cursor: pointer;
}
.record-btn.active {
  background: #ddd;
  color: #333;
}
.meta-tag {
  font-size: 0.7em;
  color: #666;
  margin-top: 5px;
  background: #eee;
  padding: 2px 5px;
  border-radius: 4px;
  display: inline-block;
}
</style>
