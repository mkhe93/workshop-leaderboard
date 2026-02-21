import { ref } from 'vue'

const backendURL = import.meta.env.VITE_BACKEND_URL

export function useCostEfficiencyData() {
  const costEfficiencyData = ref([])
  const loading = ref(false)
  const error = ref('')

  async function fetchData(startDate, endDate) {
    loading.value = true
    error.value = ''

    try {
      let url = `${backendURL}/tokens/cost-efficiency`
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
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      costEfficiencyData.value = data.cells || []
    } catch (err) {
      error.value = err.message || 'Failed to fetch cost efficiency data'
      costEfficiencyData.value = []
    } finally {
      loading.value = false
    }
  }

  function retry(startDate, endDate) {
    fetchData(startDate, endDate)
  }

  return {
    costEfficiencyData,
    loading,
    error,
    fetchData,
    retry
  }
}
