<template>
  <div class="date-range-selector">
    <div class="date-input-group">
      <label for="start-date">From:</label>
      <input
        id="start-date"
        type="date"
        :value="startDate"
        @input="$emit('update:startDate', $event.target.value)"
        :max="maxStartDate"
        class="date-input"
      />
    </div>
    <div class="date-input-group">
      <label for="end-date">To:</label>
      <input
        id="end-date"
        type="date"
        :value="endDate"
        @input="$emit('update:endDate', $event.target.value)"
        :min="startDate"
        :max="today"
        class="date-input"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  startDate: {
    type: String,
    required: true
  },
  endDate: {
    type: String,
    required: true
  }
})

defineEmits(['update:startDate', 'update:endDate'])

const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const maxStartDate = computed(() => {
  return props.endDate || today.value
})
</script>

<style scoped>
.date-range-selector {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.date-input-group label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.date-input {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: var(--font-size-xs);
  background: var(--color-surface);
  color: var(--color-text-primary);
  outline: none;
  transition: border var(--transition-base);
}

.date-input:focus {
  border: 1.5px solid var(--color-border-focus);
}

@media (max-width: 600px) {
  .date-range-selector {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
}
</style>
