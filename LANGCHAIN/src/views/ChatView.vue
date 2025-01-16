<template>
  <div class="h-screen overflow-y-scroll bg-gray-200 flex flex-col justify-between">
    <!-- 当前聊天内容区域 -->
    <div class="flex-1 space-y-4 relative">
      <!-- 消息列表 -->
      <div v-if="currentChat" class="mb-[100px]">
        <div v-for="(message, index) in currentChat.messages" :key="index" class="flex pt-4 px-10">
          <div v-if="message.isSender" class="ml-auto max-w-xs bg-sky-500 text-white p-3 rounded-[12px] shadow-md relative break-words">
            <p v-html="parseMarkdown(message.text)" class="overflow-x-auto"></p>
            <div class="absolute bottom-0 right-0 w-0 h-0 border-l-8 border-t-8 border-l-sky-500 border-t-transparent"></div>
          </div>

          <div v-else class="mr-auto max-w-xs bg-purple-500 text-white p-3 rounded-[12px] shadow-md relative break-words">
            <p v-html="parseMarkdown(message.text)" class="overflow-x-auto"></p>
            <div class="absolute bottom-0 left-0 w-0 h-0 border-r-8 border-t-8 border-r-purple-500 border-t-transparent"></div>
          </div>
        </div>
      </div>
      
      <!-- 输入区域 -->
      <div v-if="currentChat" class="p-4 bg-white flex items-center shadow-lg rounded-t-xl absolute w-full bottom-0">
        <input v-model="newMessage" type="text" placeholder="询问ai..."
          class="w-full p-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button :disabled="!canSendMessage" @click="sendMessage"
          class="ml-4 bg-purple-500 text-white p-3 rounded-lg hover:bg-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-purple-500">
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
//@ts-ignore
import { useStore } from 'vuex';
import axios from 'axios';
import { marked } from 'marked';
import { useRoute, useRouter } from 'vue-router';
import type { Message, Chat } from '../store/store';

// 获取 Vuex store
const store = useStore();

// 获取路由中的动态参数
const route = useRoute();
const router = useRouter();

// 获取当前聊天的 id 和消息列表
const currentChatId = computed(() => route.params.id as string);

// 获取当前聊天
const currentChat = computed<Chat | undefined>(() => {
  return store.state.chats.find((chat: Chat) => chat.id === currentChatId.value);
});

// 当前输入的消息
const newMessage = ref('');

// 判断是否可以发送消息
const canSendMessage = computed(() => {
  return newMessage.value.trim() !== '' && currentChat.value?.messages;
});

// 后端配置
let backendHost = import.meta.env.VITE_BACKEND_HOST;
let backendPort = import.meta.env.VITE_BACKEND_PORT;

try {
  const config = await axios.get('/config');
  if (config.status === 200) {
    backendHost = config.data.backendHost;
    backendPort = config.data.backendPort;
  }
} catch (error) {
  console.error('Failed to fetch configuration:', error);
}

// 发送消息
const sendMessage = async () => {
  if (newMessage.value.trim() && currentChat.value) {
    const message: Message = {
      text: newMessage.value,
      isSender: true,
      timestamp: new Date().toISOString()
    };

    // 将消息添加到当前聊天
    store.commit('addMessage', {
      chatId: currentChatId.value,
      message
    });

    // 清空输入框
    newMessage.value = '';

    try {
      const question = message.text;
      const response = await axios.post(`http://${backendHost}:${backendPort}/api/ask`, {
        question
      });

      // 添加后端响应的消息
      store.commit('addMessage', {
        chatId: currentChatId.value,
        message: {
          text: response.data.answer.trim() || '没有返回正确的答案',
          isSender: false,
          timestamp: new Date().toISOString()
        }
      });
    } catch (error) {
      const errorMessage = axios.isAxiosError(error)
        ? error.response?.data?.message || error.message
        : '请求失败，请稍后再试';

      store.commit('addMessage', {
        chatId: currentChatId.value,
        message: {
          text: `请求失败: ${errorMessage}`,
          isSender: false,
          timestamp: new Date().toISOString()
        }
      });
    }
  }
};

// 解析 Markdown
const parseMarkdown = (text: string) => {
  return marked(text);
};

// 组件加载时自动切换到聊天页面
onMounted(() => {
  if (!currentChat.value) {
    router.push('/'); // 如果没有找到聊天，跳转到首页
  }
});
</script>

<style scoped>
/* 自定义样式，可以根据需要调整 */
</style>
