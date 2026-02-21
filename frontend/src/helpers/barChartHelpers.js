// Bar chart color palette - distinct colors for each model
const BAR_COLORS = [
  '#FF9020', // Orange (brand color)
  '#63C1C6', // Teal
  '#FF7A7A', // Red
  '#FFB347', // Light orange
  '#7A9EFF', // Blue
  '#9D7AFF', // Purple
  '#FFD700', // Gold
  '#B0B3C6', // Gray
]

/**
 * Get mock model usage data for demo purposes
 * TEMPORARY: Hard-coded data for demo. Replace with real API data in slice 3.
 * @returns {Array} Array of {model: string, tokens: number}
 */
function getMockModelData() {
  return [
    { model: 'openai/gpt-4', tokens: 125000 },
    { model: 'anthropic/claude-3-opus', tokens: 98000 },
    { model: 'openai/gpt-3.5-turbo', tokens: 45000 },
    { model: 'anthropic/claude-3-sonnet', tokens: 32000 },
    { model: 'openai/gpt-4-turbo', tokens: 28000 }
  ]
}

/**
 * Generate distinct colors for bar chart
 * @param {number} count - Number of colors needed
 * @returns {string[]} Array of hex color codes
 */
function generateBarColors(count) {
  const colors = []
  for (let i = 0; i < count; i++) {
    colors.push(BAR_COLORS[i % BAR_COLORS.length])
  }
  return colors
}

/**
 * Transform model usage data to Chart.js bar chart format
 * @param {Array} modelData - Array of {model: string, tokens: number}
 * @returns {Object} Chart.js data object with labels and datasets
 */
function transformToBarChartData(modelData) {
  if (!modelData || modelData.length === 0) {
    return { labels: [], datasets: [] }
  }
  
  // Extract model names for x-axis labels
  const labels = modelData.map(item => item.model)
  
  // Extract token counts for bar heights
  const data = modelData.map(item => item.tokens)
  
  // Generate colors for each bar
  const colors = generateBarColors(modelData.length)
  
  return {
    labels,
    datasets: [{
      label: 'Token Usage',
      data,
      backgroundColor: colors,
      borderColor: colors,
      borderWidth: 1
    }]
  }
}

/**
 * Filter model data to only include models used by teams matching the search term
 * @param {Array} modelData - Array of {model: string, tokens: number}
 * @param {Array} teamData - Array of team objects with breakdown data
 * @param {string} searchTerm - Search term to filter teams by name
 * @returns {Array} Filtered model data
 */
function filterModelsByTeam(modelData, teamData, searchTerm) {
  // If no search term, return all models
  if (!searchTerm || searchTerm.trim() === '') {
    return modelData
  }
  
  // If no team data available, return all models (can't filter)
  if (!teamData || teamData.length === 0) {
    return modelData
  }
  
  const searchLower = searchTerm.toLowerCase().trim()
  
  // Find teams matching the search term
  const matchingTeams = teamData.filter(team => 
    team.name && team.name.toLowerCase().includes(searchLower)
  )
  
  // If no teams match, return empty array
  if (matchingTeams.length === 0) {
    return []
  }
  
  // Collect all models used by matching teams
  const modelsUsedByMatchingTeams = new Set()
  
  for (const team of matchingTeams) {
    const breakdown = team.breakdown
    if (!breakdown || !breakdown.api_keys) continue
    
    for (const apiKeyData of breakdown.api_keys) {
      const models = apiKeyData.models || []
      for (const model of models) {
        if (model.model_name) {
          modelsUsedByMatchingTeams.add(model.model_name)
        }
      }
    }
  }
  
  // Filter modelData to only include models used by matching teams
  return modelData.filter(item => modelsUsedByMatchingTeams.has(item.model))
}

export {
  BAR_COLORS,
  getMockModelData,
  generateBarColors,
  transformToBarChartData,
  filterModelsByTeam
}
