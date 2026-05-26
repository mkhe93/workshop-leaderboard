<template>
  <div class="bar-cell token-bar">
    <div class="bar-bg">
      <div
        class="bar-fg"
        :style="{ width: barWidth }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tokens: {
    type: Number,
    required: true
  },
  maxTokens: {
    type: Number,
    required: true
  }
})

const barWidth = computed(() => {
  if (props.tokens > 0 && props.maxTokens > 0) {
    return Math.round((props.tokens / props.maxTokens) * 100) + '%'
  }
  return '0%'
})
</script>

<style scoped>
.bar-cell {
  padding: var(--spacing-sm) 0;
}

.bar-bg {
  background: rgba(99, 193, 198, 0.13);
  height: 0.7em;
  width: 100%;
  border-radius: var(--radius-sm);
  margin: 0 15px;
  position: relative;
  box-shadow: var(--shadow-sm);
}

.bar-fg {
  background: linear-gradient(90deg, var(--color-primary) 60%, #ffb347 100%);
  height: 100%;
  border-radius: var(--radius-sm);
  transition: width var(--transition-slow);
  box-shadow: 0 1px 6px 0 rgba(255, 144, 32, 0.18);
}
</style>
