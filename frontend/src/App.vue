<template>
  <div class="app-wrapper">
    <div class="container">
      <div class="leaderboard-wrapper">
        <AppHeader>
          <template #title>
            <h1 class="title">Tokens Leaderboard 🏆</h1>
            <p class="subtitle-section"> AI Bootcamp </p>
          </template>
          <template #controls>
            <SharedControls @refresh="handleRefresh" />
          </template>
          <template #subtitle>
            AI Bootcamp
          </template>
        </AppHeader>
        
        <NavigationTabs />
        
        <router-view v-slot="{ Component }" ref="routerViewRef">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="refreshKey" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SharedControls from './components/SharedControls.vue'
import NavigationTabs from './components/layouts/NavigationTabs.vue'
import AppHeader from './components/layouts/AppHeader.vue'

const refreshKey = ref(0)

function handleRefresh() {
  // Force re-render of the current view by changing the key
  refreshKey.value++
}
</script>

<style>
:root {
  --color-biskaya: #242838;
}
body {
  background: var(--color-background);
  margin: 0;
  padding: 0;
  color: var(--color-text-primary);
}
.app-wrapper {
  max-width: 1000px;
  margin: 40px auto;
}
.container {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg), var(--shadow-sm);
  padding: var(--spacing-3xl) var(--spacing-xl) var(--spacing-xl) var(--spacing-xl);
}

.title {
  margin: 0;
}

.subtitle-section {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin: 0;
}

.leaderboard-wrapper {
  /* Wrapper styles */
}

@media (max-width: 1200px) {
  .container { 
    padding: var(--spacing-md) 2vw; 
  }
}

/* Fade transition for view switching */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
