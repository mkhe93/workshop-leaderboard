<script setup>
import { computed } from 'vue'
import { Bubble } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from 'chart.js'
import LoadingSpinner from '../../ui/LoadingSpinner.vue'
import ErrorMessage from '../../ui/ErrorMessage.vue'

// Register Chart.js components
ChartJS.register(
  LinearScale,
  PointElement,
  Tooltip,
  Legend
)

const props = defineProps({
  cells: {
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

// Filter cells by search term
const filteredCells = computed(() => {
  if (!props.searchTerm) return props.cells
  
  const term = props.searchTerm.toLowerCase()
  return props.cells.filter(cell => 
    cell.team.toLowerCase().includes(term) ||
    cell.model.toLowerCase().includes(term)
  )
})

// Get unique teams for color assignment
const teams = computed(() => {
  const uniqueTeams = [...new Set(filteredCells.value.map(c => c.team))]
  return uniqueTeams.sort()
})

// Color palette for teams
const teamColors = [
  'rgba(255, 99, 132, 0.7)',   // Red
  'rgba(54, 162, 235, 0.7)',   // Blue
  'rgba(255, 206, 86, 0.7)',   // Yellow
  'rgba(75, 192, 192, 0.7)',   // Teal
  'rgba(153, 102, 255, 0.7)',  // Purple
  'rgba(255, 159, 64, 0.7)',   // Orange
  'rgba(199, 199, 199, 0.7)',  // Gray
  'rgba(83, 102, 255, 0.7)',   // Indigo
  'rgba(255, 99, 255, 0.7)',   // Pink
  'rgba(99, 255, 132, 0.7)',   // Green
]

// Create color map for teams
const teamColorMap = computed(() => {
  const map = {}
  teams.value.forEach((team, index) => {
    map[team] = teamColors[index % teamColors.length]
  })
  return map
})

// Transform data for bubble chart
const bubbleChartData = computed(() => {
  // Find max cost for scaling bubbles
  const maxCost = Math.max(...filteredCells.value.map(c => c.total_cost), 1)
  
  // Calculate total cost per team
  const teamTotalCosts = {}
  filteredCells.value.forEach(cell => {
    if (!teamTotalCosts[cell.team]) {
      teamTotalCosts[cell.team] = 0
    }
    teamTotalCosts[cell.team] += cell.total_cost
  })
  
  const datasets = teams.value.map(team => {
    const teamCells = filteredCells.value.filter(c => c.team === team)
    const totalCost = teamTotalCosts[team] || 0
    
    return {
      label: `${team} ($${totalCost.toFixed(2)})`,
      data: teamCells.map(cell => ({
        x: cell.total_tokens,
        y: cell.cost_per_1k_tokens * 1000, // Convert to cost per 1M tokens
        r: Math.max(5, Math.min(40, (cell.total_cost / maxCost) * 40)), // Bubble size based on total cost
        model: cell.model,
        costPer1k: cell.cost_per_1k_tokens,
        costPer1M: cell.cost_per_1k_tokens * 1000,
        totalCost: cell.total_cost
      })),
      backgroundColor: teamColorMap.value[team],
      borderColor: teamColorMap.value[team].replace('0.7', '1'),
      borderWidth: 2
    }
  })

  return { datasets }
})

// Bubble chart options
const bubbleChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1.5,
  plugins: {
    legend: {
      display: true,
      position: 'top',
      labels: {
        color: '#f3f3f3',
        padding: 15,
        font: {
          size: 13
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(35, 37, 58, 0.95)',
      titleColor: '#f3f3f3',
      bodyColor: '#f3f3f3',
      borderColor: '#FF9020',
      borderWidth: 1,
      padding: 12,
      displayColors: true,
      callbacks: {
        title: (context) => {
          const dataPoint = context[0].raw
          return `${context[0].dataset.label} - ${dataPoint.model}`
        },
        label: (context) => {
          const dataPoint = context.raw
          return [
            `Total Cost: $${dataPoint.totalCost.toFixed(4)}`,
            `Tokens: ${dataPoint.x.toLocaleString('de-DE')}`,
            `Cost/1M: $${dataPoint.costPer1M.toFixed(2)}`
          ]
        }
      }
    }
  },
  scales: {
    x: {
      type: 'linear',
      position: 'bottom',
      grid: {
        color: 'rgba(176, 179, 198, 0.1)',
        drawBorder: false
      },
      title: {
        display: true,
        text: 'Total Tokens',
        color: '#b0b3c6',
        padding: { top: 15, bottom: 0 },
        font: {
          size: 14
        }
      },
      ticks: {
        color: '#b0b3c6',
        callback: (value) => value.toLocaleString('de-DE'),
        padding: 10
      }
    },
    y: {
      type: 'linear',
      grid: {
        color: 'rgba(176, 179, 198, 0.1)',
        drawBorder: false
      },
      title: {
        display: true,
        text: 'Cost per 1,000,000 Tokens ($)',
        color: '#b0b3c6',
        padding: { top: 0, bottom: 15 },
        font: {
          size: 14
        }
      },
      ticks: {
        color: '#b0b3c6',
        callback: (value) => `$${value.toFixed(2)}`,
        padding: 10
      }
    }
  }
}
</script>

<template>
  <div class="cost-efficiency-bubble">
    <h2 class="chart-title">Cost Efficiency Analysis</h2>
    <p class="chart-subtitle">Cost efficiency by usage (bubble size = total cost spent)</p>

    <LoadingSpinner v-if="loading" message="Loading cost efficiency data..." />

    <ErrorMessage v-else-if="error" :message="error" :showRetry="true" @retry="emit('retry')" />

    <div v-else-if="filteredCells.length === 0" class="no-data">
      No cost efficiency data available for selected filters
    </div>

    <div v-else class="chart-container">
      <Bubble :data="bubbleChartData" :options="bubbleChartOptions" />
      <div class="chart-legend-note">
        💡 Larger bubbles indicate higher total cost spent
      </div>
    </div>
  </div>
</template>

<style scoped>
.cost-efficiency-bubble {
  background: transparent;
}

.chart-title {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  font-weight: var(--font-weight-medium);
}

.chart-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-xl) 0;
}

.no-data {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-muted);
  font-size: var(--font-size-base);
}

.chart-container {
  width: 100%;
  max-width: 100%;
  min-height: 500px;
  position: relative;
}

.chart-legend-note {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--color-surface-elevated);
  border-radius: var(--radius-md);
}

@media (max-width: 768px) {
  .chart-container {
    min-height: 400px;
  }

  .chart-title {
    font-size: var(--font-size-lg);
  }

  .chart-subtitle {
    font-size: var(--font-size-xs);
  }
}
</style>
