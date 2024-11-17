// src/services/api.ts

const API_BASE = 'http://localhost:8000/api'

export const fetchSolarStats = async () => {
  try {
    const response = await fetch(`${API_BASE}/solar/stats/`)
    if (!response.ok) {
      throw new Error('Failed to fetch solar stats')
    }
    return await response.json()
  } catch (error) {
    console.error('Error fetching solar stats:', error)
    throw error
  }
}