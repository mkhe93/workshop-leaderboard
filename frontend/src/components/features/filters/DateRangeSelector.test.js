import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DateRangeSelector from './DateRangeSelector.vue'

describe('DateRangeSelector', () => {
  let mockDate

  beforeEach(() => {
    // Mock current date to 2024-02-15
    mockDate = new Date('2024-02-15T12:00:00Z')
    vi.setSystemTime(mockDate)
  })

  it('renders start and end date inputs', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const inputs = wrapper.findAll('input[type="date"]')
    expect(inputs).toHaveLength(2)
    expect(inputs[0].element.value).toBe('2024-02-01')
    expect(inputs[1].element.value).toBe('2024-02-15')
  })

  it('renders labels for date inputs', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const labels = wrapper.findAll('label')
    expect(labels).toHaveLength(2)
    expect(labels[0].text()).toBe('From:')
    expect(labels[1].text()).toBe('To:')
  })

  it('emits update:startDate when start date changes', async () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const startInput = wrapper.find('#start-date')
    await startInput.setValue('2024-02-05')
    
    expect(wrapper.emitted('update:startDate')).toBeTruthy()
    expect(wrapper.emitted('update:startDate')[0]).toEqual(['2024-02-05'])
  })

  it('emits update:endDate when end date changes', async () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const endInput = wrapper.find('#end-date')
    await endInput.setValue('2024-02-20')
    
    expect(wrapper.emitted('update:endDate')).toBeTruthy()
    expect(wrapper.emitted('update:endDate')[0]).toEqual(['2024-02-20'])
  })

  it('sets max attribute on start date to end date', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const startInput = wrapper.find('#start-date')
    expect(startInput.attributes('max')).toBe('2024-02-15')
  })

  it('sets max attribute on start date to today when no end date', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: ''
      }
    })
    
    const startInput = wrapper.find('#start-date')
    expect(startInput.attributes('max')).toBe('2024-02-15')
  })

  it('sets min attribute on end date to start date', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const endInput = wrapper.find('#end-date')
    expect(endInput.attributes('min')).toBe('2024-02-01')
  })

  it('sets max attribute on end date to today', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    const endInput = wrapper.find('#end-date')
    expect(endInput.attributes('max')).toBe('2024-02-15')
  })

  it('supports v-model binding for both dates', async () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15',
        'onUpdate:startDate': (value) => wrapper.setProps({ startDate: value }),
        'onUpdate:endDate': (value) => wrapper.setProps({ endDate: value })
      }
    })
    
    const startInput = wrapper.find('#start-date')
    await startInput.setValue('2024-02-10')
    
    expect(wrapper.emitted('update:startDate')[0]).toEqual(['2024-02-10'])
    
    const endInput = wrapper.find('#end-date')
    await endInput.setValue('2024-02-20')
    
    expect(wrapper.emitted('update:endDate')[0]).toEqual(['2024-02-20'])
  })

  it('applies correct CSS classes', () => {
    const wrapper = mount(DateRangeSelector, {
      props: {
        startDate: '2024-02-01',
        endDate: '2024-02-15'
      }
    })
    
    expect(wrapper.find('.date-range-selector').exists()).toBe(true)
    expect(wrapper.findAll('.date-input-group')).toHaveLength(2)
    expect(wrapper.findAll('.date-input')).toHaveLength(2)
  })
})
