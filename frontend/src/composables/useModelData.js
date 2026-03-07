import { ref } from 'vue'

// Shared reactive state
const modelData = ref([])
const loading = ref(false)
const error = ref('')

// In-memory cache for model data
const cache = new Map()

/**
 * Fetch model usage data with caching
 * @param {string} startDate - ISO date string (YYYY-MM-DD)
 * @param {string} endDate - ISO date string (YYYY-MM-DD)
 */
async function fetchData(startDate, endDate) {
  const cacheKey = `${startDate}-${endDate}`
  
  // Return cached data if available
  if (cache.has(cacheKey)) {
    modelData.value = cache.get(cacheKey)
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const backendURL = import.meta.env.VITE_BACKEND_URL
    
    // Build URL with query parameters
    let url = `${backendURL}/tokens/models`
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    if (params.toString()) {
      url += `?${params.toString()}`
    }

    const headers = backendURL.includes("localhost") ? {
      'Accept': 'application/json',
    } : {
      'Accept': 'application/json',
      'Authorization': `bearer ${import.meta.env.SERVER_BASIC_AUTH_TOKEN}`
    }

    const res = await fetch(url, {
      headers: headers,
      cache: 'no-store'
    })
    
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${res.status}`)
    }
    
    const responseData = await res.json()
    modelData.value = responseData.models || []
    
    // Cache the result
    cache.set(cacheKey, modelData.value)
  } catch (err) {
    error.value = err.message || 'Failed to fetch model data'
    console.error('Error fetching model data:', {
      startDate,
      endDate,
      error: err.message,
      stack: err.stack
    })
  } finally {
    loading.value = false
  }
}

/**
 * Retry the last failed fetch
 * @param {string} startDate - ISO date string (YYYY-MM-DD)
 * @param {string} endDate - ISO date string (YYYY-MM-DD)
 */
function retry(startDate, endDate) {
  // Clear error state and retry
  error.value = ''
  return fetchData(startDate, endDate)
}

/**
 * Clear the in-memory cache
 */
function invalidateCache() {
  cache.clear()
}

export function useModelData() {
  return {
    modelData,
    loading,
    error,
    fetchData,
    retry,
    invalidateCache
  }
}
