import { ref } from 'vue'
import { fetchLeaderboard } from '../helpers/helpers.js'

// Shared reactive state
const data = ref([])
const timeSeriesData = ref([])
const loading = ref(false)
const error = ref('')

// In-memory cache for data fetching
const cache = new Map()
const timeSeriesCache = new Map()

/**
 * Fetch token data with caching
 * @param {string} startDate - ISO date string (YYYY-MM-DD)
 * @param {string} endDate - ISO date string (YYYY-MM-DD)
 */
async function fetchData(startDate, endDate) {
  const cacheKey = `${startDate}-${endDate}`
  
  // Return cached data if available
  if (cache.has(cacheKey) && timeSeriesCache.has(cacheKey)) {
    data.value = cache.get(cacheKey)
    timeSeriesData.value = timeSeriesCache.get(cacheKey)
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // Fetch both aggregated and time-series data
    const [aggregatedData, timeSeriesResponse] = await Promise.all([
      fetchLeaderboard(startDate, endDate),
      fetchTimeSeries(startDate, endDate)
    ])
    
    data.value = aggregatedData
    timeSeriesData.value = timeSeriesResponse
    
    cache.set(cacheKey, aggregatedData)
    timeSeriesCache.set(cacheKey, timeSeriesResponse)
  } catch (err) {
    error.value = err.message || 'Failed to fetch data'
    console.error('Error fetching token data:', {
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
 * Fetch time-series data from backend
 * @param {string} startDate - ISO date string (YYYY-MM-DD)
 * @param {string} endDate - ISO date string (YYYY-MM-DD)
 * @returns {Promise<Array>} Time-series data
 */
async function fetchTimeSeries(startDate, endDate) {
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

  const res = await fetch(url, {
    headers: headers,
    cache: 'no-store'
  })
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP ${res.status}`)
  }
  
  const responseData = await res.json()
  return responseData.timeseries || []
}

/**
 * Clear the in-memory cache
 */
function invalidateCache() {
  cache.clear()
  timeSeriesCache.clear()
}

export function useTokenData() {
  return {
    data,
    timeSeriesData,
    loading,
    error,
    fetchData,
    retry,
    invalidateCache
  }
}
