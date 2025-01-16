<!-- 唐健峰 2024/12/22 -->
<template>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" :viewBox="viewBox" :width="size" :height="size" :fill="color">
    <path opacity=".3" d="M12 4c-4.41 0-8 3.59-8 8s3.59 8 8 8s8-3.59 8-8s-3.59-8-8-8zm5 11.59L15.59 17L12 13.41L8.41 17L7 15.59L10.59 12L7 8.41L8.41 7L12 10.59L15.59 7L17 8.41L13.41 12L17 15.59z" fill="currentColor">

    </path>
    <path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10s10-4.47 10-10S17.53 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8s8 3.59 8 8s-3.59 8-8 8zm3.59-13L12 10.59L8.41 7L7 8.41L10.59 12L7 15.59L8.41 17L12 13.41L15.59 17L17 15.59L13.41 12L17 8.41z" fill="currentColor">

    </path>
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
