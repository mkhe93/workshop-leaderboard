import { describe, expect, test, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import ChartView from './ChartsView.vue'
import { transformToChartData } from '../helpers/chartHelpers.js'

// Mock the composables
vi.mock('../composables/useFilters.js', () => ({
  useFilters: () => ({
    searchTerm: ref(''),
    startDate: ref('2024-01-01'),
    endDate: ref('2024-01-10')
  })
}))

vi.mock('../composables/useTokenData.js', () => ({
  useTokenData: () => ({
    data: ref([
      { 
        name: 'Team A', 
        tokens: 1000,
        breakdown: {
          api_keys: [{
            api_key: 'key1',
            models: [{
              model_name: 'gpt-4',
              prompt_tokens: 500,
              completion_tokens: 500,
              total_tokens: 1000
            }]
          }]
        }
      },
      { 
        name: 'Team B', 
        tokens: 1500,
        breakdown: {
          api_keys: [{
            api_key: 'key2',
            models: [{
              model_name: 'gpt-3.5-turbo',
              prompt_tokens: 750,
              completion_tokens: 750,
              total_tokens: 1500
            }]
          }]
        }
      },
      { 
        name: 'Team C', 
        tokens: 800,
        breakdown: {
          api_keys: [{
            api_key: 'key3',
            models: [{
              model_name: 'gpt-4',
              prompt_tokens: 400,
              completion_tokens: 400,
              total_tokens: 800
            }]
          }]
        }
      }
    ]),
    timeSeriesData: ref([
      {
        date: '2024-01-01',
        teams: [
          { name: 'Team A', tokens: 1000 },
          { name: 'Team B', tokens: 1500 },
          { name: 'Team C', tokens: 800 }
        ]
      },
      {
        date: '2024-01-02',
        teams: [
          { name: 'Team A', tokens: 1200 },
          { name: 'Team B', tokens: 1400 },
          { name: 'Team C', tokens: 900 }
        ]
      },
      {
        date: '2024-01-03',
        teams: [
          { name: 'Team A', tokens: 1100 },
          { name: 'Team B', tokens: 1600 },
          { name: 'Team C', tokens: 850 }
        ]
      }
    ]),
    loading: ref(false),
    error: ref(''),
    fetchData: vi.fn(),
    retry: vi.fn()
  })
}))

vi.mock('../composables/useModelData.js', () => ({
  useModelData: () => ({
    modelData: ref([
      { model: 'gpt-4', tokens: 5000 },
      { model: 'gpt-3.5-turbo', tokens: 3000 }
    ]),
    loading: ref(false),
    error: ref(''),
    fetchData: vi.fn(),
    retry: vi.fn()
  })
}))

vi.mock('../composables/useTeamSuccessRateData.js', () => ({
  useTeamSuccessRateData: () => ({
    successRateData: ref([
      { 
        name: 'Team A', 
        total_requests: 100, 
        successful_requests: 95, 
        failed_requests: 5 
      },
      { 
        name: 'Team B', 
        total_requests: 150, 
        successful_requests: 132, 
        failed_requests: 18 
      }
    ]),
    loading: ref(false),
    error: ref(''),
    fetchData: vi.fn(),
    retry: vi.fn()
  })
}))

vi.mock('../composables/useCostEfficiencyData.js', () => ({
  useCostEfficiencyData: () => ({
    costEfficiencyData: ref([
      { team: 'Team A', model: 'gpt-4', cost_per_1k_tokens: 0.03, total_cost: 150, total_tokens: 5000000 },
      { team: 'Team B', model: 'gpt-3.5-turbo', cost_per_1k_tokens: 0.002, total_cost: 30, total_tokens: 15000000 }
    ]),
    loading: ref(false),
    error: ref(''),
    fetchData: vi.fn(),
    retry: vi.fn()
  })
}))

// Mock Chart.js components
vi.mock('vue-chartjs', () => ({
  Bar: {
    name: 'Bar',
    template: '<div class="mock-chart"></div>',
    props: ['data', 'options']
  },
  Doughnut: {
    name: 'Doughnut',
    template: '<div class="mock-chart"></div>',
    props: ['data', 'options']
  },
  Line: {
    name: 'Line',
    template: '<div class="mock-chart"></div>',
    props: ['data', 'options']
  },
  Bubble: {
    name: 'Bubble',
    template: '<div class="mock-chart"></div>',
    props: ['data', 'options']
  }
}))

// Mock chart components
vi.mock('../components/features/charts/TokenTypeBreakdown.vue', () => ({
  default: {
    name: 'TokenTypeBreakdown',
    template: '<div class="token-type-breakdown"></div>',
    props: ['teams', 'loading', 'error', 'searchTerm']
  }
}))

vi.mock('../components/features/charts/RequestSuccessSummary.vue', () => ({
  default: {
    name: 'RequestSuccessSummary',
    template: '<div class="request-success-summary"></div>',
    props: ['successRateSummary', 'loading', 'error', 'searchTerm']
  }
}))

vi.mock('../components/features/charts/CostEfficiencyHeatmap.vue', () => ({
  default: {
    name: 'CostEfficiencyHeatmap',
    template: '<div class="cost-efficiency-heatmap"></div>',
    props: ['cells', 'loading', 'error', 'searchTerm']
  }
}))

vi.mock('../components/features/charts/ModelUsageChart.vue', () => ({
  default: {
    name: 'ModelUsageChart',
    template: '<div class="model-usage-chart"></div>',
    props: ['chartData', 'loading', 'error']
  }
}))

vi.mock('../components/features/charts/ModelFilter.vue', () => ({
  default: {
    name: 'ModelFilter',
    template: '<div class="model-filter"></div>',
    props: ['availableModels', 'selectedModels', 'visible']
  }
}))

describe('ChartView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders without errors with mock data', () => {
    // when
    const wrapper = mount(ChartView)

    // then
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.chart-view').exists()).toBe(true)
  })

  test('creates correct number of datasets for teams', () => {
    // given
    const mockTimeSeriesData = [
      {
        date: '2024-01-01',
        teams: [
          { name: 'Team A', tokens: 1000 },
          { name: 'Team B', tokens: 1500 },
          { name: 'Team C', tokens: 800 }
        ]
      },
      {
        date: '2024-01-02',
        teams: [
          { name: 'Team A', tokens: 1200 },
          { name: 'Team B', tokens: 1400 },
          { name: 'Team C', tokens: 900 }
        ]
      }
    ]

    // when
    const chartData = transformToChartData(mockTimeSeriesData)

    // then
    expect(chartData.datasets).toHaveLength(3)
    expect(chartData.datasets[0].label).toBe('Team A')
    expect(chartData.datasets[1].label).toBe('Team B')
    expect(chartData.datasets[2].label).toBe('Team C')
  })

  test('displays chart container when data is available', () => {
    // when
    const wrapper = mount(ChartView)

    // then
    expect(wrapper.find('.chart-view').exists()).toBe(true)
    expect(wrapper.find('.chart-section').exists()).toBe(true)
  })

  test('does not display loading or error states when data is present', async () => {
    // when
    const wrapper = mount(ChartView)
    await wrapper.vm.$nextTick()

    // then
    expect(wrapper.find('.loading').exists()).toBe(false)
    expect(wrapper.find('.error').exists()).toBe(false)
    expect(wrapper.find('.no-data').exists()).toBe(false)
  })
})
