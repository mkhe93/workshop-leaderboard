<script setup>
// AppHeader component with title and controls slots
</script>

<template>
  <div class="app-header">
    <div class="header-content">
      <div class="title-section">
        <slot name="title">
          <!-- Default title content -->
        </slot>
      </div>
      <div class="controls-section">
        <slot name="controls">
          <!-- Header controls like search, date range, etc. -->
        </slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-header {
  margin-bottom: var(--spacing-xl);
}

.header-content {
  display: flex;
  align-items: start;
  justify-content: space-between;
  margin-bottom: var(--spacing-xl);
}

.title-section h1 {
  font-size: var(--font-size-2xl);
  color: var(--color-text-primary);
  letter-spacing: 0.01em;
  margin: 0;
}

.subtitle-section {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-xl);
  margin-top: var(--spacing-xl);
}

@media (max-width: 800px) {
  .title-section h1 {
    font-size: var(--font-size-lg);
  }
}
</style>
