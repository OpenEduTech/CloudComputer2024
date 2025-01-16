<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Left Sidebar -->
    <div :class="sidebarClass" 
         class="content-blue h-full transition-all duration-300 bg-gradient-to-r from-blue-500 to-indigo-600 p-4 shadow-xl relative flex flex-col justify-between"
         @mouseover="showCancelIcon" 
         @mouseleave="hideCancelIcon">
      <div class="flex items-center justify-between w-full mb-6">
        <h2 v-if="!isSidebarCollapsed" class="text-xl font-semibold text-white">历史记录</h2>
        <button @click="toggleSidebar" class="text-white hover:text-gray-300 focus:outline-none rounded-full transition-all duration-200 hover:bg-white/20">
          <span v-if="isSidebarCollapsed">
            <CollapsibleSidebarIcon :size="'32'" />
          </span>
          <span v-else>
            <CancelIcon v-if="showCancel" :size="'20'" />
          </span>
        </button>
      </div>

      <!-- Chat List -->
      <div v-if="!isSidebarCollapsed" class="mt-6 space-y-2 overflow-y-scroll">
        <div v-for="chat in chats" :key="chat.id" class="p-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
          <RouterLink :to="`/chat/${chat.id}`" class="text-lg block font-medium text-blue-800 hover:text-blue-600">
            聊天 - {{ chat.id }}
          </RouterLink>
        </div>
      </div>

      <!-- 新聊天按钮 -->
      <div v-if="!isSidebarCollapsed" class="rounded-lg shadow-md mt-2">
        <button @click="createNewChat" class="bg-blue-400 text-white p-3 rounded-lg hover:bg-blue-600 transition-colors w-full text-center">
          新聊天
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-sky flex-1 bg-gradient-to-t from-indigo-100 h-screen to-white">
      <Suspense>
        <RouterView />
      </Suspense>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import CollapsibleSidebarIcon from '../components/icons/CollapsibleSidebarIcon.vue';
import CancelIcon from '../components/icons/CancelIcon.vue';
//@ts-ignore
import { useStore } from 'vuex';

const store = useStore();
const router = useRouter();
const isSidebarCollapsed = ref(false);
const showCancel = ref(false);

// 获取聊天列表
const chats = computed(() => store.state.chats);

// 切换左侧栏折叠状态
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

// 创建新聊天
const createNewChat = () => {
  store.dispatch('createNewChat');
  const latestChat = store.state.chats[store.state.chats.length - 1];
  store.commit('setCurrentChatId', latestChat.id); // 设置当前聊天ID
  // 跳转到新聊天页面
  router.push(`/chat/${latestChat.id}`);
};

// 显示 CancelIcon
const showCancelIcon = () => {
  showCancel.value = true;
};

// 隐藏 CancelIcon
const hideCancelIcon = () => {
  showCancel.value = false;
};

// 计算属性：根据是否折叠改变类名
const sidebarClass = computed(() => {
  return isSidebarCollapsed.value ? 'w-16' : 'w-64';
});
</script>

<style scoped>
/* 侧边栏样式 */
.content-blue {
  background: linear-gradient(to bottom right, #9333ea, #3b82f6);
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.1);
}
</style>
