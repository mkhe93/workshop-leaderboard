<template>
  <div class="leaderboard-view">
    <LeaderboardTable
      :teams="filteredTeams"
      :maxTokens="maxTokens"
      :expandedTeams="expandedTeams"
      @toggle-expand="toggleExpand"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useFilters } from '../composables/useFilters'
import { useTokenData } from '../composables/useTokenData'
import { filterTeamsByName } from '../helpers/helpers'
import LeaderboardTable from '../components/features/leaderboard/LeaderboardTable.vue'

// Use shared filters from composable
const { searchTerm, startDate, endDate } = useFilters()

// Use shared token data from composable
const { data: teams, retry: retryFetch } = useTokenData()

// Local state
const expandedTeams = ref(new Set())

// Fetch leaderboard data
async function refresh() {
  await retryFetch(startDate.value, endDate.value)
}

// Computed filtered teams
const filteredTeams = computed(() =>
  filterTeamsByName(teams.value, searchTerm.value)
)

// Computed max tokens for bar scaling
const maxTokens = computed(() =>
  teams.value.length
    ? Math.max(...teams.value.map(t => t.tokens), 1)
    : 1
)

// Expansion state management
function toggleExpand(teamName) {
  if (expandedTeams.value.has(teamName)) {
    expandedTeams.value.delete(teamName)
  } else {
    expandedTeams.value.add(teamName)
  }
  expandedTeams.value = new Set(expandedTeams.value)
}

// Watch date changes and trigger refresh
watch([startDate, endDate], () => {
  if (startDate.value && endDate.value) {
    refresh()
  }
})

// Initial fetch when mounted
onMounted(() => {
  if (startDate.value && endDate.value) {
    refresh()
  }
})
</script>

<style scoped>
.leaderboard-view {
  /* View wrapper */
}
</style>
