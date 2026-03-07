import { describe, expect, test } from 'vitest'

import { applyMedals, maskApiKey } from './helpers'

describe('applyMedals', () => {
  test('applies gold, silver, and bronze to top 3 teams with tokens > 0', () => {
    // given
    const input = [
      {name: 'Group 1', tokens: 10},
      {name: 'Group 2', tokens: 5},
      {name: 'Group 3', tokens: 1},
      {name: 'Group 4', tokens: 0}
    ]

    // when
    const result = applyMedals(input)

    // then
    expect(result[0].medal).toBe('🥇')
    expect(result[1].medal).toBe('🥈')
    expect(result[2].medal).toBe('🥉')
    expect(result[3].medal).toBeUndefined()
  })
})

describe('maskApiKey - Edge Cases', () => {
  test('masks API key with standard length correctly', () => {
    // Standard OpenAI-style key
    const key = 'sk-1234567890abcdef'
    const result = maskApiKey(key)
    expect(result).toBe('sk-...cdef')
  })

  test('returns original key when length is less than 10 characters', () => {
    // Edge case: short API key (< 10 chars)
    const shortKey = 'sk-123'
    const result = maskApiKey(shortKey)
    expect(result).toBe('sk-123')
  })

  test('returns original key when length is exactly 10 characters', () => {
    // Edge case: exactly 10 chars (boundary)
    const boundaryKey = 'sk-123456'  // Exactly 10 chars
    const result = maskApiKey(boundaryKey)
    expect(result).toBe('sk-123456')
  })

  test('masks key with length of 11 characters', () => {
    // Edge case: just above boundary (11 chars)
    const key = 'sk-12345678'
    const result = maskApiKey(key)
    expect(result).toBe('sk-...5678')
  })

  test('handles null or undefined gracefully', () => {
    // Edge case: null input
    expect(maskApiKey(null)).toBe(null)
    
    // Edge case: undefined input
    expect(maskApiKey(undefined)).toBe(undefined)
  })

  test('handles empty string', () => {
    // Edge case: empty string
    const result = maskApiKey('')
    expect(result).toBe('')
  })

  test('masks very long API keys correctly', () => {
    // Edge case: very long key
    const longKey = 'sk-' + 'a'.repeat(100)
    const result = maskApiKey(longKey)
    expect(result).toBe('sk-...' + 'a'.repeat(4))
  })
})
