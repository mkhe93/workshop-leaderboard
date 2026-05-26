<template>
  <div class="request-success-summary">
    <h2 class="chart-title">Request Success Rate Summary</h2>
    <p class="chart-subtitle">Overall success rate per team for selected time frame</p>
    
    <LoadingSpinner v-if="loading" message="Loading success rate data..." />
    <ErrorMessage v-else-if="error" :message="error" :showRetry="true" @retry="emit('retry')" />
    <div v-else-if="filteredTeams.length === 0" class="no-data">
      <p>No request data available for selected filters</p>
    </div>
    <div v-else class="charts-container">
      <div v-for="team in filteredTeams" :key="team.name" class="chart-card">
        <h3 class="team-name">{{ team.name }}</h3>
        <div class="chart-wrapper">
          <Doughnut :data="getChartData(team)" :options="chartOptions" />
        </div>
        <div class="team-stats">
          <div class="stat">
            <span class="stat-label">Total:</span>
            <span class="stat-value">{{ team.total_requests.toLocaleString('de-DE') }}</span>
          </div>
          <div class="stat success">
            <span class="stat-label">Success:</span>
            <span class="stat-value">{{ team.successful_requests.toLocaleString('de-DE') }}</span>
          </div>
          <div class="stat failed">
            <span class="stat-label">Failed:</span>
            <span class="stat-value">{{ team.failed_requests.toLocaleString('de-DE') }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'
import LoadingSpinner from '../../ui/LoadingSpinner.vue'
import ErrorMessage from '../../ui/ErrorMessage.vue'

// Register Chart.js components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

const props = defineProps({
  successRateSummary: {
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
  if (!props.successRateSummary || props.successRateSummary.length === 0) return []
  
  // Filter out teams with zero total requests
  let teams = props.successRateSummary.filter(team => team.total_requests > 0)
  
  if (!props.searchTerm || !props.searchTerm.trim()) return teams
  
  // Split by comma, trim, and filter out empty terms
  const terms = props.searchTerm
    .split(',')
    .map(t => t.trim().toLowerCase())
    .filter(t => t.length > 0)
  
  if (terms.length === 0) return teams
  
  // Filter teams by search terms
  return teams.filter(team =>
    terms.some(term => team.name.toLowerCase().includes(term))
  )
})

// Generate chart data for a specific team
function getChartData(team) {
  return {
    labels: ['Successful', 'Failed'],
    datasets: [{
      data: [team.successful_requests, team.failed_requests],
      backgroundColor: [
        '#2ECC71', // Green for success
        '#E74C3C'  // Red for failed
      ],
      borderColor: [
        '#27AE60',
        '#C0392B'
      ],
      borderWidth: 2
    }]
  }
}

// Chart.js configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 1,
  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        color: '#f3f3f3',
        padding: 12,
        font: {
          size: 12
        },
        usePointStyle: true,
        pointStyle: 'circle'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(35, 37, 58, 0.95)',
      titleColor: '#f3f3f3',
      bodyColor: '#f3f3f3',
      borderColor: '#FF9020',
      borderWidth: 1,
      padding: 12,
      callbacks: {
        label: (context) => {
          const label = context.label || ''
          const value = context.parsed
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
          return `${label}: ${value.toLocaleString('de-DE')} (${percentage}%)`
        }
      }
    }
  }
}
</script>

<style scoped>
.request-success-summary {
  background: transparent;
  padding: var(--spacing-xl) 0;
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
  font-style: italic;
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-lg);
  width: 100%;
  max-width: 100%;
}

.chart-card {
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: var(--transition-base);
  min-width: 0;
  overflow: hidden;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.team-name {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
  font-weight: var(--font-weight-medium);
  text-align: center;
  width: 100%;
  min-height: 2.4em;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1.2;
}

.chart-wrapper {
  width: 100%;
  max-width: 200px;
  margin: 0 auto var(--spacing-md);
}

.team-stats {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  width: 100%;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xs) 0;
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

.stat-value {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.stat.success .stat-value {
  color: #2ECC71;
}

.stat.failed .stat-value {
  color: var(--color-error);
}

.no-data {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-muted);
  font-size: var(--font-size-base);
}

/* Responsive breakpoints */
@media (max-width: 1400px) {
  .charts-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 1024px) {
  .charts-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .chart-title {
    font-size: var(--font-size-lg);
  }
  
  .chart-subtitle {
    font-size: var(--font-size-xs);
  }
  
  .chart-card {
    padding: var(--spacing-lg);
  }
  
  .chart-wrapper {
    max-width: 150px;
  }
}
</style>
