<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()

const activeView = computed(() => route.name)

function handleNavigate(view) {
  router.push({ name: view })
}
</script>

<template>
  <div class="navigation-tabs">
    <button 
      :class="{ active: activeView === 'leaderboard' }"
      @click="handleNavigate('leaderboard')"
    >
      Leaderboard
    </button>
    <button 
      :class="{ active: activeView === 'chart' }"
      @click="handleNavigate('chart')"
    >
      Charts
    </button>
  </div>
</template>

<style scoped>
.navigation-tabs {
  display: flex;
  gap: 0;
  background: var(--color-surface-elevated);
  border-bottom: 2px solid var(--color-border);
}

.navigation-tabs button {
  padding: var(--spacing-lg) var(--spacing-2xl);
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--transition-base);
  margin-bottom: -2px;
  flex: 1;
}

.navigation-tabs button:hover {
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.navigation-tabs button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  background: var(--color-primary-light);
}
</style>
