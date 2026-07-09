<script setup lang="ts">
defineProps<{
  visible: boolean
  countdown: number
}>()

const emit = defineEmits<{
  continue: []
}>()
</script>

<template>
  <div v-if="visible" class="idle-popup">
    <div class="popup-box">
      <p>
        60秒間操作がありませんでした。<br />
        続行しますか？
      </p>

      <p class="count">
        タイマー: {{ countdown }}s
      </p>

      <div class="popup-buttons">
        <button @click="emit('continue')">
          Yes
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* move your popup css here */
</style>