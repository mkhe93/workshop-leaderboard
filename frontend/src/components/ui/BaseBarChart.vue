<template>
  <div class="base-bar-chart">
    <!-- Title and Subtitle -->
    <h2 v-if="title" class="chart-title">{{ title }}</h2>
    <p v-if="subtitle" class="chart-subtitle">{{ subtitle }}</p>
    
    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Loading chart data..." />
    
    <!-- Error State -->
    <ErrorMessage 
      v-else-if="error" 
      :message="error" 
      :showRetry="true" 
      @retry="emit('retry')" 
    />
    
    <!-- No Data State -->
    <div v-else-if="chartData.datasets.length === 0 || chartData.labels.length === 0" class="no-data">
      No data available for selected filters
    </div>
    
    <!-- Chart State -->
    <div v-else class="chart-container">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import LoadingSpinner from './LoadingSpinner.vue'
import ErrorMessage from './ErrorMessage.vue'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

// Props definition
const props = defineProps({
  // Data
  chartData: {
    type: Object,
    required: true,
    default: () => ({ labels: [], datasets: [] })
  },
  
  // State
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  
  // Display
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  
  // Customization
  xAxisTitle: {
    type: String,
    default: ''
  },
  yAxisTitle: {
    type: String,
    default: ''
  },
  yAxisFormatter: {
    type: Function,
    default: null
  },
  options: {
    type: Object,
    default: () => ({})
  },
  
  // Stacked mode
  stacked: {
    type: Boolean,
    default: false
  },
  showLegend: {
    type: Boolean,
    default: undefined
  }
})

// Events
const emit = defineEmits(['retry'])

// Deep merge function for options
const deepMerge = (target, source) => {
  const output = { ...target }
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target)) {
          output[key] = source[key]
        } else {
          output[key] = deepMerge(target[key], source[key])
        }
      } else {
        output[key] = source[key]
      }
    })
  }
  
  return output
}

const isObject = (item) => {
  return item && typeof item === 'object' && !Array.isArray(item)
}

// Get the formatter to use (custom or default)
const getFormatter = () => {
  return props.yAxisFormatter || formatTokenValue
}

// German locale formatter for y-axis values
const formatTokenValue = (value) => {
  return value.toLocaleString('de-DE')
}

// Computed property for Chart.js configuration
const chartOptions = computed(() => {
  const formatter = getFormatter()
  
  // Determine legend visibility
  // Show legend if stacked is true OR showLegend is explicitly true
  const shouldShowLegend = props.stacked || props.showLegend === true
  
  // Determine interaction mode based on stacked
  const interactionMode = props.stacked ? 'index' : 'nearest'
  
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1.5,
    interaction: {
      mode: interactionMode,
      axis: 'x',
      intersect: false
    },
    layout: {
      padding: {
        left: 10,
        right: 10,
        top: 10,
        bottom: 20
      }
    },
    plugins: {
      legend: {
        display: shouldShowLegend,
        position: 'top',
        labels: {
          color: '#f3f3f3',
          padding: 15,
          font: {
            size: 14
          },
          usePointStyle: true,
          pointStyle: 'rect'
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
          label: (context) => {
            const label = context.dataset.label || context.label || ''
            const value = formatter(context.parsed.y)
            return label ? `${label}: ${value} tokens` : `${value} tokens`
          }
        }
      }
    },
    scales: {
      x: {
        stacked: props.stacked,
        grid: {
          color: 'rgba(176, 179, 198, 0.1)',
          drawBorder: false
        },
        title: {
          display: true,
          text: props.xAxisTitle || 'Category',
          color: '#b0b3c6',
          padding: { top: 15, bottom: 0 },
          font: {
            size: 20
          }
        },
        ticks: {
          color: '#b0b3c6',
          padding: 10,
          maxRotation: 45,
          minRotation: 0
        }
      },
      y: {
        stacked: props.stacked,
        grid: {
          color: 'rgba(176, 179, 198, 0.1)',
          drawBorder: false
        },
        title: {
          display: true,
          text: props.yAxisTitle || 'Tokens',
          color: '#b0b3c6',
          padding: { top: 0, bottom: 15 },
          font: {
            size: 20
          }
        },
        ticks: {
          color: '#b0b3c6',
          padding: 10,
          callback: function(value) {
            return formatter(value)
          }
        }
      }
    }
  }
  
  // Merge custom options with defaults (custom options take precedence)
  return deepMerge(defaultOptions, props.options)
})
</script>

<style scoped>
.base-bar-chart {
  width: 100%;
  background: transparent;
}

.chart-title {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg) 0;
  font-weight: var(--font-weight-medium);
}

.chart-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: calc(var(--spacing-lg) * -0.5) 0 var(--spacing-lg) 0;
}

.chart-container {
  width: 100%;
  max-width: 100%;
  min-height: 500px;
  position: relative;
}

.no-data {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--color-text-muted);
  font-size: var(--font-size-base);
}

@media (max-width: 768px) {
  .chart-container {
    min-height: 400px;
  }
  
  .chart-title {
    font-size: var(--font-size-lg);
  }
}
</style>
