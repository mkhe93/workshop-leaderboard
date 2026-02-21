import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchInput from './SearchInput.vue'
import BaseInput from '../../ui/BaseInput.vue'

describe('SearchInput', () => {
  it('renders with default placeholder', () => {
    const wrapper = mount(SearchInput)
    
    const baseInput = wrapper.findComponent(BaseInput)
    expect(baseInput.exists()).toBe(true)
    expect(baseInput.props('placeholder')).toBe('Search...')
  })

  it('renders with custom placeholder', () => {
    const wrapper = mount(SearchInput, {
      props: {
        placeholder: 'Search teams...'
      }
    })
    
    const baseInput = wrapper.findComponent(BaseInput)
    expect(baseInput.props('placeholder')).toBe('Search teams...')
  })

  it('binds modelValue correctly', () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'test search'
      }
    })
    
    const baseInput = wrapper.findComponent(BaseInput)
    expect(baseInput.props('modelValue')).toBe('test search')
  })

  it('emits update:modelValue when input changes', async () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: ''
      }
    })
    
    const baseInput = wrapper.findComponent(BaseInput)
    await baseInput.vm.$emit('update:modelValue', 'new value')
    
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['new value'])
  })

  it('supports v-model binding', async () => {
    const wrapper = mount(SearchInput, {
      props: {
        modelValue: 'initial',
        'onUpdate:modelValue': (value) => wrapper.setProps({ modelValue: value })
      }
    })
    
    const baseInput = wrapper.findComponent(BaseInput)
    await baseInput.vm.$emit('update:modelValue', 'updated')
    
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['updated'])
  })

  it('passes autocomplete="off" to BaseInput', () => {
    const wrapper = mount(SearchInput)
    
    const input = wrapper.find('input')
    expect(input.attributes('autocomplete')).toBe('off')
  })

  it('applies search-input class', () => {
    const wrapper = mount(SearchInput)
    
    expect(wrapper.find('.search-input').exists()).toBe(true)
  })
})
