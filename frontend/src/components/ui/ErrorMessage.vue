<template>
  <div class="error-message">
    <div class="error-message__icon">⚠️</div>
    <p class="error-message__text">{{ message }}</p>
    <BaseButton
      v-if="showRetry"
      variant="secondary"
      @click="handleRetry"
      class="error-message__retry"
    >
      Retry
    </BaseButton>
  </div>
</template>

<script setup>
import BaseButton from './BaseButton.vue'

defineProps({
  message: {
    type: String,
    required: true
  },
  showRetry: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['retry'])

const handleRetry = () => {
  emit('retry')
}
</script>

<style scoped>
.error-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  background: var(--color-surface);
  border: 1px solid var(--color-error);
  border-radius: var(--radius-lg);
  text-align: center;
}

.error-message__icon {
  font-size: var(--font-size-2xl);
}

.error-message__text {
  margin: 0;
  color: var(--color-error);
  font-size: var(--font-size-base);
}

.error-message__retry {
  margin-top: var(--spacing-sm);
}
</style>
