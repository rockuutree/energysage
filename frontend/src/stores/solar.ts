import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SolarState } from '../types'
import { fetchSolarStats } from '../services/api'

export const useSolarStore = defineStore('solar', () => {
  const solarData = ref<SolarState[]>([])
  const selectedState = ref<SolarState | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchSolarData = async () => {
    loading.value = true
    error.value = null
    try {
      solarData.value = await fetchSolarStats()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch solar data'
      console.error('Error fetching solar data:', e)
    } finally {
      loading.value = false
    }
  }

  const selectState = (state: SolarState) => {
    selectedState.value = state
  }

  const getStateByCode = (stateCode: string) => {
    return solarData.value.find(state => state.state === stateCode)
  }

  return {
    solarData,
    selectedState,
    loading,
    error,
    fetchSolarData,
    selectState,
    getStateByCode
  }
})