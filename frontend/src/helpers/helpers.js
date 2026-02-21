function applyMedals(sortedTeams) {
  const medalByIndex = ['🥇','🥈','🥉']
  return sortedTeams.map((t, idx) => ({
    ...t,
    medal: t.tokens > 0 && idx < 3 ? medalByIndex[idx] : undefined
  }))
}

async function fetchLeaderboard(startDate = null, endDate = null) {
  const backendURL = import.meta.env.VITE_BACKEND_URL;
  
  // Build URL with query parameters
  let url = `${backendURL}/tokens`;
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  const headers = backendURL.includes("localhost") ? {
        'Accept': 'application/json',
    } : {
        'Accept': 'application/json',
        'Authorization': `bearer ${import.meta.env.SERVER_BASIC_AUTH_TOKEN}`
    };

  const res = await fetch(url, {
    headers: headers,
    cache: 'no-store'
  });
  
  if (!res.ok) {
    // Try to extract error message from backend
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${res.status}`);
  }
  
  const data = await res.json();
  const incomingTeams = Array.isArray(data.teams) ? data.teams : [];
  const sorted = [...incomingTeams].sort((a, b) => b.tokens - a.tokens);
  return applyMedals(sorted);
}

function filterTeamsByName(teams, searchTerm) {
  if (!searchTerm || !searchTerm.trim()) return teams;
  // Split by comma, trim, and filter out empty terms
  const terms = searchTerm
    .split(',')
    .map(t => t.trim().toLowerCase())
    .filter(t => t.length > 0);
  if (terms.length === 0) return teams;
  return teams.filter(team =>
    terms.some(term => team.name.toLowerCase().includes(term))
  );
}

/**
 * Mask API key for display (show first 3 and last 4 characters)
 * Example: sk-1234567890abcdef -> sk-...cdef
 */
function maskApiKey(apiKey) {
  if (!apiKey || apiKey.length < 10) {
    return apiKey  // Too short to mask meaningfully
  }
  const prefix = apiKey.substring(0, 3)
  const suffix = apiKey.substring(apiKey.length - 4)
  return `${prefix}...${suffix}`
}

/**
 * Debounce function - delays execution until after wait milliseconds have elapsed
 * since the last time it was invoked
 * @param {Function} func - The function to debounce
 * @param {number} wait - The number of milliseconds to delay
 * @returns {Function} The debounced function
 */
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

export { applyMedals, fetchLeaderboard, filterTeamsByName, maskApiKey, debounce }
