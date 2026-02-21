<template>
  <div class="token-type-breakdown">
    <BaseBarChart
      :chartData="barChartData"
      :loading="loading"
      :error="error"
      :stacked="true"
      title="Token Type Breakdown by Team"
      subtitle="Prompt tokens (input) vs Completion tokens (output)"
      xAxisTitle="Team"
      @retry="emit('retry')"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import BaseBarChart from '../../ui/BaseBarChart.vue'

const props = defineProps({
  teams: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  searchTerm: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['retry'])

// Apply search filter to teams
const filteredTeams = computed(() => {
  if (!props.teams || props.teams.length === 0) return []
  if (!props.searchTerm || !props.searchTerm.trim()) return props.teams
  
  // Split by comma, trim, and filter out empty terms
  const terms = props.searchTerm
    .split(',')
    .map(t => t.trim().toLowerCase())
    .filter(t => t.length > 0)
  
  if (terms.length === 0) return props.teams
  
  return props.teams.filter(team =>
    terms.some(term => team.name.toLowerCase().includes(term))
  )
})

// Transform team data into chart format
const chartData = computed(() => {
  if (filteredTeams.value.length === 0) return []
  
  return filteredTeams.value
    .map(team => {
      // Calculate totals from breakdown
      let promptTokens = 0
      let completionTokens = 0
      
      if (team.breakdown?.api_keys) {
        team.breakdown.api_keys.forEach(apiKey => {
          apiKey.models.forEach(model => {
            promptTokens += model.prompt_tokens || 0
            completionTokens += model.completion_tokens || 0
          })
        })
      }
      
      return {
        name: team.name,
        promptTokens,
        completionTokens,
        total: promptTokens + completionTokens
      }
    })
    .filter(team => team.total > 0) // Only show teams with data
    .sort((a, b) => b.total - a.total) // Sort by total tokens descending
})

// Prepare data for Chart.js stacked bar
const barChartData = computed(() => {
  const labels = chartData.value.map(t => t.name)
  
  return {
    labels,
    datasets: [
      {
        label: 'Prompt Tokens',
        data: chartData.value.map(t => t.promptTokens),
        backgroundColor: '#63C1C6',
        borderColor: '#63C1C6',
        borderWidth: 0
      },
      {
        label: 'Completion Tokens',
        data: chartData.value.map(t => t.completionTokens),
        backgroundColor: '#FF9020',
        borderColor: '#FF9020',
        borderWidth: 0
      }
    ]
  }
})
</script>

<style scoped>
.token-type-breakdown {
  background: transparent;
  padding: var(--spacing-xl) 0;
}
</style>
