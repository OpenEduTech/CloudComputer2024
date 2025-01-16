<script setup lang="ts">
import {
    RouterLink,
    RouterView
} from 'vue-router'
import {
    NConfigProvider,
    NGlobalStyle
} from 'naive-ui';
</script>

<template>
    
<NConfigProvider :theme-overrides="{
      common: {
        fontFamily: 'sans-serif' // 你想要的字体
      }
    }">
    <NGlobalStyle />
    <header class="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-4 shadow-lg">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <!-- 左侧 Logo 或者文字 -->
            <div class="text-2xl font-semibold">
                <img src="./assets/ecnu.svg" alt="Logo" class="h-14 w-auto">
            </div>

            <!-- 导航栏 -->
            <nav class="space-x-6">
                <RouterLink to="/" class="hover:text-gray-400 transition-colors text-lg">Home</RouterLink>
            </nav>
        </div>
    </header>
    
    <Suspense>
        <RouterView />
    </Suspense>
</NConfigProvider>
</template>

<style>
</style>
