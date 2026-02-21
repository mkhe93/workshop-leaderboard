<template>
  <div class="team-name" @click="$emit('click')">
    <span class="expand-icon">{{ isExpanded ? '▼' : '▶' }}</span>
    {{ team.name }} <span v-if="team.medal" class="medal">{{ team.medal }}</span>
  </div>
  <TokenBar :tokens="team.tokens" :maxTokens="maxTokens" />
  <div class="token-count">{{ formatNumber(team.tokens) }}</div>
</template>

<script setup>
import TokenBar from './TokenBar.vue'

defineProps({
  team: {
    type: Object,
    required: true
  },
  maxTokens: {
    type: Number,
    required: true
  },
  isExpanded: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

function formatNumber(n) {
  return n.toLocaleString('de-DE')
}
</script>

<style scoped>
.team-name,
.token-count {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: var(--spacing-md) var(--spacing-sm);
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  text-shadow: 0 1px 2px #181a28;
}

.team-name {
  cursor: pointer;
  user-select: none;
}

.expand-icon {
  display: inline-block;
  width: 1em;
  margin-right: 0.5em;
  font-size: 0.8em;
  color: var(--color-primary);
}

.token-count {
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  text-shadow: 0 1px 2px #181a28;
}

@media (max-width: 800px) {
  .team-name, .token-count {
    font-size: var(--font-size-base);
    padding: var(--spacing-sm) 2px;
  }
}
</style>
