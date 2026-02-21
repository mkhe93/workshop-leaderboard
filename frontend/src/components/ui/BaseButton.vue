<template>
  <button
    :class="['base-button', `base-button--${variant}`, { 'base-button--disabled': disabled, 'base-button--loading': loading }]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="base-button__spinner"></span>
    <span :class="{ 'base-button__content--hidden': loading }">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.base-button {
  font-family: var(--font-family);
  /* font-size: var(--font-size-base); */
  font-weight: var(--font-weight-medium);
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.base-button--primary {
  background: var(--color-primary);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-primary);
}

.base-button--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.base-button--secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.base-button--secondary:hover:not(:disabled) {
  background: var(--color-surface-elevated);
  border-color: var(--color-primary);
}

.base-button--danger {
  background: var(--color-error);
  color: var(--color-text-primary);
}

.base-button--danger:hover:not(:disabled) {
  background: var(--color-error-dark);
  transform: translateY(-1px);
}

.base-button--disabled,
.base-button--loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.base-button__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  position: absolute;
}

.base-button__content--hidden {
  visibility: hidden;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
