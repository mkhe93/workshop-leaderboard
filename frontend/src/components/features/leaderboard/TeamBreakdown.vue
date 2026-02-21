<template>
  <div class="breakdown-section">
    <div v-if="hasBreakdown" class="breakdown-content">
      <div v-for="keyData in sortedApiKeys" :key="keyData.api_key" class="api-key-section">
        <div class="api-key-header">
          {{ keyData.key_alias || maskApiKey(keyData.api_key) }}
        </div>
        <div class="models-list">
          <div v-for="model in keyData.models" :key="model.model_name" class="model-row">
            <span class="model-name">{{ model.model_name }}</span>
            <span class="model-tokens">{{ formatNumber(model.total_tokens) }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="no-breakdown">
      No detailed breakdown available
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { maskApiKey } from '../../../helpers/helpers'

const props = defineProps({
  breakdown: {
    type: Object,
    default: null
  }
})

const hasBreakdown = computed(() => {
  return props.breakdown && 
         props.breakdown.api_keys && 
         props.breakdown.api_keys.length > 0
})

const sortedApiKeys = computed(() => {
  if (!hasBreakdown.value) {
    return []
  }
  return [...props.breakdown.api_keys].sort((a, b) => {
    const keyA = a.key_alias || a.api_key
    const keyB = b.key_alias || b.api_key
    return keyA.localeCompare(keyB)
  })
})

function formatNumber(n) {
  return n.toLocaleString('de-DE')
}
</script>

<style scoped>
.breakdown-section {
  grid-column: 1 / -1;
  padding: var(--spacing-xl) var(--spacing-2xl);
  background: var(--color-surface-elevated);
  border-left: 4px solid var(--color-primary);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  margin: 0 0 var(--spacing-lg) 0;
  box-shadow: var(--shadow-md);
}

.breakdown-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.api-key-section {
  background: rgba(255, 255, 255, 0.05);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-primary-light);
  transition: all var(--transition-base);
}

.api-key-section:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 144, 32, 0.25);
  box-shadow: 0 2px 6px rgba(255, 144, 32, 0.1);
}

.api-key-header {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
  font-family: monospace;
  font-weight: var(--font-weight-semibold);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid rgba(255, 144, 32, 0.2);
}

.models-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding-left: var(--spacing-xl);
}

.model-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.model-row:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateX(2px);
}

.model-name {
  color: var(--color-text-primary);
  font-size: 0.95rem;
  flex: 1;
}

.model-tokens {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
  text-align: right;
  min-width: 100px;
  padding-left: var(--spacing-lg);
}

.no-breakdown {
  color: var(--color-text-secondary);
  font-style: italic;
  text-align: center;
  padding: var(--spacing-xl);
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
}

@media (max-width: 800px) {
  .breakdown-section {
    padding: var(--spacing-md) var(--spacing-lg);
  }
  
  .api-key-header {
    font-size: var(--font-size-xs);
  }
  
  .model-row {
    font-size: var(--font-size-sm);
  }
}

@media (max-width: 600px) {
  .breakdown-section {
    padding: var(--spacing-lg);
    margin: 0 0 var(--spacing-md) 0;
    border-left-width: 3px;
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
  }
  
  .breakdown-content {
    gap: var(--spacing-lg);
  }
  
  .api-key-section {
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
  }
  
  .api-key-header {
    font-size: 0.8rem;
    margin-bottom: var(--spacing-sm);
    padding-bottom: 0.4rem;
    word-break: break-all;
  }
  
  .models-list {
    padding-left: var(--spacing-md);
    gap: 0.4rem;
  }
  
  .model-row {
    padding: var(--spacing-sm) 0.6rem;
    font-size: var(--font-size-sm);
    flex-wrap: nowrap;
  }
  
  .model-name {
    font-size: var(--font-size-sm);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    min-width: 0;
  }
  
  .model-tokens {
    font-size: var(--font-size-sm);
    min-width: 80px;
    padding-left: var(--spacing-sm);
    flex-shrink: 0;
  }
  
  .no-breakdown {
    padding: var(--spacing-lg);
    font-size: var(--font-size-sm);
  }
}
</style>
