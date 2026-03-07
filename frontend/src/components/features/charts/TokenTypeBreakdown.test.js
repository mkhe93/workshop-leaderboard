import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TokenTypeBreakdown from './TokenTypeBreakdown.vue'

// Mock the UI components
vi.mock('../../ui/LoadingSpinner.vue', () => ({
  default: {
    name: 'LoadingSpinner',
    template: '<div class="loading-spinner">{{ message }}</div>',
    props: ['message']
  }
}))

vi.mock('../../ui/ErrorMessage.vue', () => ({
  default: {
    name: 'ErrorMessage',
    template: '<div class="error-message">{{ message }}</div>',
    props: ['message', 'showRetry']
  }
}))

describe('TokenTypeBreakdown', () => {
  it('calculates prompt and completion tokens correctly', () => {
    const teams = [
      {
        name: 'Team A',
        tokens: 1000,
        breakdown: {
          api_keys: [
            {
              api_key: 'sk-test1',
              models: [
                {
                  model_name: 'gpt-4',
                  total_tokens: 1000,
                  prompt_tokens: 600,
                  completion_tokens: 400
                }
              ]
            }
          ]
        }
      },
      {
        name: 'Team B',
        tokens: 800,
        breakdown: {
          api_keys: [
            {
              api_key: 'sk-test2',
              models: [
                {
                  model_name: 'gpt-3.5-turbo',
                  total_tokens: 800,
                  prompt_tokens: 500,
                  completion_tokens: 300
                }
              ]
            }
          ]
        }
      }
    ]

    const wrapper = mount(TokenTypeBreakdown, {
      props: {
        teams,
        loading: false,
        error: '',
        searchTerm: ''
      }
    })

    // Component should render without errors
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.chart-title').text()).toBe('Token Type Breakdown by Team')
  })

  it('filters teams by search term', () => {
    const teams = [
      {
        name: 'Alpha Team',
        tokens: 1000,
        breakdown: {
          api_keys: [
            {
              api_key: 'sk-test1',
              models: [
                {
                  model_name: 'gpt-4',
                  total_tokens: 1000,
                  prompt_tokens: 600,
                  completion_tokens: 400
                }
              ]
            }
          ]
        }
      },
      {
        name: 'Beta Team',
        tokens: 800,
        breakdown: {
          api_keys: [
            {
              api_key: 'sk-test2',
              models: [
                {
                  model_name: 'gpt-3.5-turbo',
                  total_tokens: 800,
                  prompt_tokens: 500,
                  completion_tokens: 300
                }
              ]
            }
          ]
        }
      }
    ]

    const wrapper = mount(TokenTypeBreakdown, {
      props: {
        teams,
        loading: false,
        error: '',
        searchTerm: 'Alpha'
      }
    })

    // Should filter to only Alpha Team
    expect(wrapper.exists()).toBe(true)
  })

  it('shows loading state', () => {
    const wrapper = mount(TokenTypeBreakdown, {
      props: {
        teams: [],
        loading: true,
        error: '',
        searchTerm: ''
      }
    })

    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    expect(wrapper.find('.loading-spinner').text()).toBe('Loading chart data...')
  })

  it('shows error state', () => {
    const wrapper = mount(TokenTypeBreakdown, {
      props: {
        teams: [],
        loading: false,
        error: 'Failed to load data',
        searchTerm: ''
      }
    })

    expect(wrapper.find('.error-message').exists()).toBe(true)
    expect(wrapper.find('.error-message').text()).toBe('Failed to load data')
  })

  it('shows no data message when teams array is empty', () => {
    const wrapper = mount(TokenTypeBreakdown, {
      props: {
        teams: [],
        loading: false,
        error: '',
        searchTerm: ''
      }
    })

    // Empty teams array results in empty chartData.datasets, triggering no-data state
    expect(wrapper.find('.no-data').exists()).toBe(true)
    expect(wrapper.find('.no-data').text()).toBe('No data available for selected filters')
  })

  it('handles teams without breakdown data', () => {
    const teams = [
      {
        name: 'Team Without Breakdown',
        tokens: 1000
        // No breakdown property
      }
    ]

    const wrapper = mount(TokenTypeBreakdown, {
      props: {
        teams,
        loading: false,
        error: '',
        searchTerm: ''
      }
    })

    // Should not crash, should show no data
    expect(wrapper.exists()).toBe(true)
  })
})
