<script setup>
import { computed, watch, onMounted, ref } from 'vue'
import { useFilters } from '../composables/useFilters.js'
import { useTokenData } from '../composables/useTokenData.js'
import { useModelData } from '../composables/useModelData.js'
import { useTeamSuccessRateData } from '../composables/useTeamSuccessRateData.js'
import { useCostEfficiencyData } from '../composables/useCostEfficiencyData.js'
import { transformToBarChartData, filterModelsByTeam } from '../helpers/barChartHelpers.js'
import TokenTypeBreakdown from '../components/features/charts/TokenTypeBreakdown.vue'
import RequestSuccessSummary from '../components/features/charts/RequestSuccessSummary.vue'
import CostEfficiencyHeatmap from '../components/features/charts/CostEfficiencyHeatmap.vue'
import ModelUsageChart from '../components/features/charts/ModelUsageChart.vue'
import ModelFilter from '../components/features/charts/ModelFilter.vue'

// Get shared state
const { searchTerm, startDate, endDate } = useFilters()
const { data, loading: tokenLoading, error: tokenError, fetchData: fetchTokenData } = useTokenData()
const { 
  modelData, 
  loading: modelLoading, 
  error: modelError, 
  fetchData: fetchModelData, 
  retry: retryModelFetch 
} = useModelData()
const {
  successRateData,
  loading: successRateLoading,
  error: successRateError,
  fetchData: fetchSuccessRateData
} = useTeamSuccessRateData()
const {
  costEfficiencyData,
  loading: costEfficiencyLoading,
  error: costEfficiencyError,
  fetchData: fetchCostEfficiencyData,
  retry: retryCostEfficiencyFetch
} = useCostEfficiencyData()

// Model filter state
const selectedModels = ref(new Set())
const showModelFilter = ref(false)

// Get unique models for filter
const availableModels = computed(() => {
  if (!modelData.value || modelData.value.length === 0) return []
  return modelData.value.map(m => m.model)
})

// Toggle model selection
function toggleModel(model) {
  if (selectedModels.value.has(model)) {
    selectedModels.value.delete(model)
  } else {
    selectedModels.value.add(model)
  }
  // Trigger reactivity
  selectedModels.value = new Set(selectedModels.value)
}

// Select all models
function selectAllModels() {
  selectedModels.value = new Set(availableModels.value)
}

// Clear all model selections
function clearAllModels() {
  selectedModels.value = new Set()
}

// Compute bar chart data from real API data with search filter and model filter applied
const barChartData = computed(() => {
  if (!modelData.value || modelData.value.length === 0) {
    return { labels: [], datasets: [] }
  }
  
  // Apply search filter using team data
  let filteredModelData = filterModelsByTeam(
    modelData.value,
    data.value,  // Team data with breakdown
    searchTerm.value
  )
  
  // Apply model filter if any models are selected
  if (selectedModels.value.size > 0) {
    filteredModelData = filteredModelData.filter(m => selectedModels.value.has(m.model))
  }
  
  return transformToBarChartData(filteredModelData)
})

// Watch date range changes - fetch immediately (no debounce for date changes)
watch([startDate, endDate], () => {
  if (startDate.value && endDate.value) {
    fetchTokenData(startDate.value, endDate.value)
    fetchModelData(startDate.value, endDate.value)
    fetchSuccessRateData(startDate.value, endDate.value)
    fetchCostEfficiencyData(startDate.value, endDate.value)
  }
})

// Initial data fetch
onMounted(() => {
  if (startDate.value && endDate.value) {
    fetchTokenData(startDate.value, endDate.value)
    fetchModelData(startDate.value, endDate.value)
    fetchSuccessRateData(startDate.value, endDate.value)
    fetchCostEfficiencyData(startDate.value, endDate.value)
  }
})

// Retry function for model data error state
function retryModel() {
  if (startDate.value && endDate.value) {
    retryModelFetch(startDate.value, endDate.value)
  }
}

// Retry function for cost efficiency data error state
function retryCostEfficiency() {
  if (startDate.value && endDate.value) {
    retryCostEfficiencyFetch(startDate.value, endDate.value)
  }
}

// Retry function for token data error state
function retryTokenData() {
  if (startDate.value && endDate.value) {
    fetchTokenData(startDate.value, endDate.value)
  }
}

// Retry function for success rate data error state
function retrySuccessRate() {
  if (startDate.value && endDate.value) {
    fetchSuccessRateData(startDate.value, endDate.value)
  }
}
</script>

<template>
  <div class="chart-view">
    <!-- Request Success Rate Summary -->
    <div class="chart-section">
      <RequestSuccessSummary
        :successRateSummary="successRateData"
        :loading="successRateLoading"
        :error="successRateError"
        :searchTerm="searchTerm"
        @retry="retrySuccessRate"
      />
    </div>

    <!-- Cost Efficiency Heatmap -->
    <div class="chart-section">
      <CostEfficiencyHeatmap
        :cells="costEfficiencyData"
        :loading="costEfficiencyLoading"
        :error="costEfficiencyError"
        :searchTerm="searchTerm"
        @retry="retryCostEfficiency"
      />
    </div>

    <!-- Token Type Breakdown Chart -->
    <div class="chart-section">
      <TokenTypeBreakdown 
        :teams="data" 
        :loading="tokenLoading" 
        :error="tokenError"
        :searchTerm="searchTerm"
        @retry="retryTokenData"
      />
    </div>

    <!-- Model Usage Chart -->
    <div class="chart-section chart-selector">
      <ModelFilter
        :availableModels="availableModels"
        :selectedModels="selectedModels"
        :visible="showModelFilter"
        @toggle-model="toggleModel"
        @select-all="selectAllModels"
        @clear-all="clearAllModels"
        @toggle-visibility="showModelFilter = !showModelFilter"
      />

      <ModelUsageChart
        :chartData="barChartData"
        :loading="modelLoading"
        :error="modelError"
        @retry="retryModel"
      />
    </div>
  </div>
</template>

<style scoped>
.chart-view {
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3xl);
  padding-top: var(--spacing-xl);
}

.chart-section {
  background: transparent;
}

/* Responsive adjustments for mobile devices */
@media (max-width: 768px) {
  .chart-view {
    gap: var(--spacing-2xl);
  }
}
</style>
