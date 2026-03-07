<template>
  <div class="shared-controls">
    <div class="controls-top">
      <SearchInput
        v-model="searchTerm"
        placeholder="Search teams (comma-separated)"
      />
      <BaseButton 
        variant="primary" 
        @click="$emit('refresh')" 
        class="refresh-button"
        title="Refresh data"
      >
        Refresh
      </BaseButton>
      <slot></slot>
    </div>
    <div class="date-range">
      <DateRangeSelector
        v-model:startDate="startDate"
        v-model:endDate="endDate"
      />
    </div>
  </div>
</template>

<script setup>
import { useFilters } from '../composables/useFilters'
import SearchInput from './features/filters/SearchInput.vue'
import DateRangeSelector from './features/filters/DateRangeSelector.vue'
import BaseButton from './ui/BaseButton.vue'

const { searchTerm, startDate, endDate } = useFilters()

defineEmits(['refresh'])
</script>

<style scoped>
.shared-controls {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.controls-top {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  justify-content: flex-end;
}

.date-range {
  display: flex;
  justify-content: flex-end;
}

.refresh-button {
  flex-shrink: 0;
  height: auto;
  line-height: 1;
}

@media (max-width: 600px) {
  .shared-controls {
    width: 100%;
  }
  
  .refresh-button {
    font-size: var(--font-size-base);
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
</style>
