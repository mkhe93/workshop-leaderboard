// Chart.js color palette for team lines
const CHART_COLORS = [
  '#FF9020', // Orange (brand color)
  '#63C1C6', // Teal
  '#FF7A7A', // Red
  '#FFB347', // Light orange
  '#7A9EFF', // Blue
  '#B0B3C6', // Gray
  '#9D7AFF', // Purple
  '#FFD700', // Gold
]

/**
 * Get color for a team based on its index
 * @param {number} index - Team index
 * @returns {string} Hex color code
 */
function getTeamColor(index) {
  return CHART_COLORS[index % CHART_COLORS.length]
}

/**
 * Generate array of dates between startDate and endDate (inclusive)
 * @param {string} startDate - ISO date string (YYYY-MM-DD)
 * @param {string} endDate - ISO date string (YYYY-MM-DD)
 * @returns {string[]} Array of ISO date strings
 */
function generateDateRange(startDate, endDate) {
  const dates = []
  const start = new Date(startDate)
  const end = new Date(endDate)
  
  const current = new Date(start)
  while (current <= end) {
    dates.push(current.toISOString().split('T')[0])
    current.setDate(current.getDate() + 1)
  }
  
  return dates
}

/**
 * Transform time-series data to Chart.js format
 * @param {Array} timeSeriesData - Array of {date, teams: [{name, tokens}]}
 * @returns {Object} Chart.js data object with labels and datasets
 */
function transformToChartData(timeSeriesData) {
  if (!timeSeriesData || timeSeriesData.length === 0) {
    return { labels: [], datasets: [] }
  }
  
  // Extract dates for x-axis labels
  const labels = timeSeriesData.map(point => {
    const date = new Date(point.date)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })
  
  // Build a map of team name -> array of token counts
  const teamDataMap = new Map()
  
  timeSeriesData.forEach(point => {
    point.teams.forEach(team => {
      if (!teamDataMap.has(team.name)) {
        teamDataMap.set(team.name, [])
      }
      teamDataMap.get(team.name).push(team.tokens)
    })
  })
  
  // Convert to Chart.js datasets format
  const datasets = []
  let colorIndex = 0
  
  teamDataMap.forEach((data, teamName) => {
    datasets.push({
      label: teamName,
      data: data,
      borderColor: getTeamColor(colorIndex),
      backgroundColor: getTeamColor(colorIndex),
      tension: 0.1
    })
    colorIndex++
  })
  
  return { labels, datasets }
}

export {
  CHART_COLORS,
  getTeamColor,
  generateDateRange,
  transformToChartData
}
