<template>
  <div class="leaderboard">
    <template v-for="team in teams" :key="team.name">
      <TeamRow
        :team="team"
        :maxTokens="maxTokens"
        :isExpanded="expandedTeams.has(team.name)"
        @click="toggleExpand(team.name)"
      />
      <TeamBreakdown
        v-if="expandedTeams.has(team.name)"
        :breakdown="team.breakdown"
      />
    </template>
  </div>
</template>

<script setup>
import TeamRow from './TeamRow.vue'
import TeamBreakdown from './TeamBreakdown.vue'

defineProps({
  teams: {
    type: Array,
    required: true
  },
  maxTokens: {
    type: Number,
    required: true
  },
  expandedTeams: {
    type: Set,
    required: true
  }
})

const emit = defineEmits(['toggle-expand'])

function toggleExpand(teamName) {
  emit('toggle-expand', teamName)
}
</script>

<style scoped>
.leaderboard {
  display: grid;
  grid-template-columns: max-content 1fr max-content;
  gap: var(--spacing-lg);
  align-items: center;
  padding-top: var(--spacing-2xl);
}
</style>
