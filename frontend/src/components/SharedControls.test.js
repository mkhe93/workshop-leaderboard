import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import SharedControls from './SharedControls.vue'
import SearchInput from './features/filters/SearchInput.vue'
import DateRangeSelector from './features/filters/DateRangeSelector.vue'

// Mock the useFilters composable
vi.mock('../composables/useFilters', () => ({
  useFilters: vi.fn()
}))

describe('SharedControls', () => {
  let mockSearchTerm
  let mockStartDate
  let mockEndDate

  beforeEach(async () => {
    // Create mock refs for the composable
    mockSearchTerm = ref('')
    mockStartDate = ref('2024-02-01')
    mockEndDate = ref('2024-02-15')

    // Setup the mock to return our refs
    const { useFilters } = await import('../composables/useFilters')
    useFilters.mockReturnValue({
      searchTerm: mockSearchTerm,
      startDate: mockStartDate,
      endDate: mockEndDate
    })
  })

  it('renders SearchInput component', () => {
    const wrapper = mount(SharedControls)
    
    const searchInput = wrapper.findComponent(SearchInput)
    expect(searchInput.exists()).toBe(true)
  })

  it('renders DateRangeSelector component', () => {
    const wrapper = mount(SharedControls)
    
    const dateRangeSelector = wrapper.findComponent(DateRangeSelector)
    expect(dateRangeSelector.exists()).toBe(true)
  })

  it('binds searchTerm from useFilters to SearchInput', () => {
    mockSearchTerm.value = 'test search'
    
    const wrapper = mount(SharedControls)
    const searchInput = wrapper.findComponent(SearchInput)
    
    expect(searchInput.props('modelValue')).toBe('test search')
  })

  it('binds dates from useFilters to DateRangeSelector', () => {
    const wrapper = mount(SharedControls)
    const dateRangeSelector = wrapper.findComponent(DateRangeSelector)
    
    expect(dateRangeSelector.props('startDate')).toBe('2024-02-01')
    expect(dateRangeSelector.props('endDate')).toBe('2024-02-15')
  })

  it('updates searchTerm when SearchInput emits update', async () => {
    const wrapper = mount(SharedControls)
    const searchInput = wrapper.findComponent(SearchInput)
    
    await searchInput.vm.$emit('update:modelValue', 'new search')
    
    expect(mockSearchTerm.value).toBe('new search')
  })

  it('updates startDate when DateRangeSelector emits update', async () => {
    const wrapper = mount(SharedControls)
    const dateRangeSelector = wrapper.findComponent(DateRangeSelector)
    
    await dateRangeSelector.vm.$emit('update:startDate', '2024-02-10')
    
    expect(mockStartDate.value).toBe('2024-02-10')
  })

  it('updates endDate when DateRangeSelector emits update', async () => {
    const wrapper = mount(SharedControls)
    const dateRangeSelector = wrapper.findComponent(DateRangeSelector)
    
    await dateRangeSelector.vm.$emit('update:endDate', '2024-02-20')
    
    expect(mockEndDate.value).toBe('2024-02-20')
  })

  it('passes custom placeholder to SearchInput', () => {
    const wrapper = mount(SharedControls)
    const searchInput = wrapper.findComponent(SearchInput)
    
    expect(searchInput.props('placeholder')).toBe('Search teams (comma-separated)')
  })

  it('renders default slot content', () => {
    const wrapper = mount(SharedControls, {
      slots: {
        default: '<button>Extra Control</button>'
      }
    })
    
    expect(wrapper.html()).toContain('<button>Extra Control</button>')
  })

  it('applies correct CSS structure', () => {
    const wrapper = mount(SharedControls)
    
    expect(wrapper.find('.shared-controls').exists()).toBe(true)
    expect(wrapper.find('.controls-top').exists()).toBe(true)
    expect(wrapper.find('.date-range').exists()).toBe(true)
  })

  it('places SearchInput and slot in controls-top', () => {
    const wrapper = mount(SharedControls, {
      slots: {
        default: '<div class="test-slot">Test</div>'
      }
    })
    
    const controlsTop = wrapper.find('.controls-top')
    expect(controlsTop.findComponent(SearchInput).exists()).toBe(true)
    expect(controlsTop.find('.test-slot').exists()).toBe(true)
  })

  it('places DateRangeSelector in date-range section', () => {
    const wrapper = mount(SharedControls)
    
    const dateRange = wrapper.find('.date-range')
    expect(dateRange.findComponent(DateRangeSelector).exists()).toBe(true)
  })
})
