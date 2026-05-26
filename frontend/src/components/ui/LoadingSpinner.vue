<template>
  <div :class="['loading-spinner', `loading-spinner--${size}`]">
    <div class="loading-spinner__circle"></div>
    <p v-if="message" class="loading-spinner__message">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  message: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}

.loading-spinner__circle {
  border-radius: 50%;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  animation: spin 0.8s linear infinite;
}

.loading-spinner--small .loading-spinner__circle {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.loading-spinner--medium .loading-spinner__circle {
  width: 40px;
  height: 40px;
  border-width: 3px;
}

.loading-spinner--large .loading-spinner__circle {
  width: 64px;
  height: 64px;
  border-width: 4px;
}

.loading-spinner__message {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
