import { ref } from 'vue'

// Shared reactive state
const timeseriesData = ref([])
const loading = ref(false)
const error = ref('')

// In-memory cache for timeseries data
const cache = new Map()

/**
 * Fetch timeseries data with caching
 * @param {string} startDate - ISO date string (YYYY-MM-DD)
 * @param {string} endDate - ISO date string (YYYY-MM-DD)
 */
async function fetchData(startDate, endDate) {
  const cacheKey = `${startDate}-${endDate}`
  
  // Return cached data if available
  if (cache.has(cacheKey)) {
    timeseriesData.value = cache.get(cacheKey)
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const backendURL = import.meta.env.VITE_BACKEND_URL
    
    // Build URL with query parameters
    let url = `${backendURL}/tokens/timeseries`
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

    const response = await fetch(url, {
      headers: headers,
      cache: 'no-store'
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    timeseriesData.value = data.timeseries || []
    
    // Cache the result
    cache.set(cacheKey, timeseriesData.value)
  } catch (err) {
    error.value = err.message || 'Failed to fetch timeseries data'
    timeseriesData.value = []
    console.error('Error fetching timeseries data:', {
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

export function useTimeseriesData() {
  return {
    timeseriesData,
    loading,
    error,
    fetchData,
    retry,
    invalidateCache
  }
}
