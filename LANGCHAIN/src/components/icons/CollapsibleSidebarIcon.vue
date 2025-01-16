<!-- 唐健峰 2024/12/22 -->
<template>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" :viewBox="viewBox" :width="size" :height="size" :fill="color">
    <g fill="none">
        <path d="M5 6a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1zm0 4a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1zm0 4a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1zm0 4a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1z" fill="currentColor"></path>
    </g>
</svg>
</template>

  
<script setup lang="ts">
defineProps({
    color: {
        type: String,
        default: 'black', // 默认颜色为 currentColor，可以继承父元素的文本颜色
    },
    size: {
        type: String,
        default: '24', // 默认大小为 24px
    },
    viewBox: {
        type: String,
        default: '0 0 24 24', // 默认视口大小
    },
});
</script>

  
<style scoped>
/* 你可以在这里为组件添加样式，例如设置图标的默认颜色或大小 */
</style>
