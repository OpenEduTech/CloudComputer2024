<template>
    <div class="flex flex-col items-center justify-center space-y-6 h-full">
        <h2 class="text-4xl font-extrabold text-gray-800"
            style="font-family: 'Poppins', sans-serif; letter-spacing: 1px; line-height: 1.5; text-shadow: 2px 2px 4px rgba(0, 0, 255, 0.3), 4px 4px 6px rgba(75, 0, 130, 0.3);">
            AI Chat
        </h2>
        <p class="text-lg text-gray-600">云计算 RAG</p>
        <!-- Button with animation and shadow -->
        <button
            class="px-6 py-3 bg-indigo-600 text-white font-semibold text-lg rounded-lg shadow-lg transition-transform transform hover:scale-105 hover:shadow-2xl focus:outline-none">
            <div @click="createNewChat" class="hover:text-gray-400 transition-colors text-lg">点击开始</div>
        </button>
    </div>
</template>
<script setup lang="ts">
import { useRouter } from 'vue-router';
//@ts-ignore
import { useStore } from 'vuex';
const store = useStore();
const router = useRouter();
// 创建新聊天
const createNewChat = () => {
    store.dispatch('createNewChat');
    const latestChat = store.state.chats[store.state.chats.length - 1];
    store.commit('setCurrentChatId', latestChat.id);  // 设置当前聊天ID
    // 跳转到新聊天页面
    router.push(`/chat/${latestChat.id}`);
  };
</script>
<style scoped></style>