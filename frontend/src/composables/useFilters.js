import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// LocalStorage keys
const STORAGE_KEY_START = 'leaderboard_start_date'
const STORAGE_KEY_END = 'leaderboard_end_date'
const STORAGE_KEY_SEARCH = 'leaderboard_search_term'
const STORAGE_KEY_VIEW = 'leaderboard_current_view'

// Shared reactive state
const searchTerm = ref('')
const startDate = ref('')
const endDate = ref('')

// Router instances (will be set on first use)
let router = null
let route = null

// Initialize dates to last 24 hours
function setDefaultDates() {
  const end = new Date()
  const start = new Date(end)
  start.setDate(start.getDate() - 1)
  
  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0]
  }
}

// Load from localStorage
function loadFromStorage() {
  const savedStart = localStorage.getItem(STORAGE_KEY_START)
  const savedEnd = localStorage.getItem(STORAGE_KEY_END)
  const savedSearch = localStorage.getItem(STORAGE_KEY_SEARCH)
  
  if (savedStart && savedEnd) {
    startDate.value = savedStart
    endDate.value = savedEnd
  } else {
    const defaults = setDefaultDates()
    startDate.value = defaults.start
    endDate.value = defaults.end
  }
  
  if (savedSearch) {
    searchTerm.value = savedSearch
  }
}

// Save current view to localStorage
function saveCurrentView(viewName) {
  localStorage.setItem(STORAGE_KEY_VIEW, viewName)
}

// Load saved view from localStorage
function loadSavedView() {
  return localStorage.getItem(STORAGE_KEY_VIEW) || 'leaderboard'
}

// Save to localStorage
function saveToStorage() {
  localStorage.setItem(STORAGE_KEY_START, startDate.value)
  localStorage.setItem(STORAGE_KEY_END, endDate.value)
  localStorage.setItem(STORAGE_KEY_SEARCH, searchTerm.value)
}

// Sync filters from URL query parameters
function syncWithURL() {
  if (!route) return
  
  const query = route.query
  
  // Read from URL query params if present
  if (query.search !== undefined) {
    searchTerm.value = query.search
  }
  if (query.start !== undefined) {
    startDate.value = query.start
  }
  if (query.end !== undefined) {
    endDate.value = query.end
  }
}

// Update URL with current filter values
function updateURL() {
  if (!router) return
  
  // Build query object with current filter values
  const query = {}
  
  if (searchTerm.value) {
    query.search = searchTerm.value
  }
  if (startDate.value) {
    query.start = startDate.value
  }
  if (endDate.value) {
    query.end = endDate.value
  }
  
  // Use router.replace to avoid adding history entries
  router.replace({ query }).catch(() => {
    // Ignore navigation duplicated errors
  })
}

// Initialize state on first use
let initialized = false

export function useFilters() {
  // Set router instances on first use
  if (!router) {
    router = useRouter()
    route = useRoute()
  }
  
  if (!initialized) {
    // First try to load from URL (takes precedence)
    syncWithURL()
    
    // Then load from localStorage for any missing values
    loadFromStorage()
    
    // Navigate to saved view if not already on a specific route
    if (route.path === '/') {
      const savedView = loadSavedView()
      router.replace(`/${savedView}`)
    }
    
    initialized = true
    
    // Watch for changes and auto-save to both localStorage and URL
    watch([searchTerm, startDate, endDate], () => {
      saveToStorage()
      updateURL()
    })
    
    // Watch route changes to save current view
    watch(() => route.name, (newView) => {
      if (newView) {
        saveCurrentView(newView)
      }
    })
  }
  
  return {
    searchTerm,
    startDate,
    endDate
  }
}
