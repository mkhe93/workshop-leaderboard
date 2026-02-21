<template>
  <div class="model-filter">
    <div class="filter-header">
      <h3 class="filter-title">Filter by Model</h3>
      <button 
        @click="emit('toggle-visibility')" 
        class="filter-toggle-button"
      >
        {{ visible ? 'Hide' : 'Show' }} Filter
        <span class="filter-count" v-if="selectedModels.size > 0">({{ selectedModels.size }})</span>
      </button>
    </div>

    <div v-if="visible && availableModels.length > 0" class="model-filter-panel">
      <div class="filter-actions">
        <button @click="emit('select-all')" class="filter-action-btn">Select All</button>
        <button @click="emit('clear-all')" class="filter-action-btn">Clear All</button>
      </div>
      <div class="model-checkboxes">
        <label 
          v-for="model in availableModels" 
          :key="model"
          class="model-checkbox-label"
        >
          <input 
            type="checkbox" 
            :checked="selectedModels.has(model)"
            @change="emit('toggle-model', model)"
            class="model-checkbox"
          />
          <span class="model-name">{{ model }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  availableModels: {
    type: Array,
    required: true,
    default: () => []
  },
  selectedModels: {
    type: Set,
    required: true,
    default: () => new Set()
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-model', 'select-all', 'clear-all', 'toggle-visibility'])
</script>

<style scoped>
.model-filter {
  margin-bottom: var(--spacing-lg);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.filter-title {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin: 0;
  font-weight: var(--font-weight-medium);
}

.filter-toggle-button {
  padding: var(--spacing-sm) var(--spacing-lg);
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 2px solid var(--color-text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.filter-toggle-button:hover {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.filter-count {
  background-color: var(--color-primary);
  color: white;
  padding: 2px var(--spacing-sm);
  border-radius: 12px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.model-filter-panel {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.filter-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.filter-action-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: var(--transition-base);
}

.filter-action-btn:hover {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.model-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--spacing-sm);
  max-height: 300px;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.model-checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-sm);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition-base);
}

.model-checkbox-label:hover {
  background-color: var(--color-border);
}

.model-checkbox {
  cursor: pointer;
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.model-name {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  user-select: none;
}

@media (max-width: 768px) {
  .model-checkboxes {
    grid-template-columns: 1fr;
  }

  .filter-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-toggle-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
