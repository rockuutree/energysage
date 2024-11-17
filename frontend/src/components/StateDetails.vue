<template>
  <div class="bg-white p-4 rounded-lg shadow-lg">
    <h2 class="text-xl font-bold mb-4">State Details</h2>
    <div v-if="stateData">
      <h3 class="text-lg font-semibold mb-3">{{ stateData.state }}</h3>
      <div class="space-y-4">
        <div class="p-3 bg-gray-50 rounded">
          <div class="text-sm text-gray-600">Total Capacity</div>
          <div class="text-lg font-semibold">
            {{ formatNumber(stateData.total_capacity_ac) }} MW
          </div>
        </div>
        <div class="p-3 bg-gray-50 rounded">
          <div class="text-sm text-gray-600">Number of Installations</div>
          <div class="text-lg font-semibold">
            {{ stateData.installation_count }}
          </div>
        </div>
        <div class="p-3 bg-gray-50 rounded">
          <div class="text-sm text-gray-600">Average Capacity</div>
          <div class="text-lg font-semibold">
            {{ formatNumber(stateData.avg_capacity) }} MW
          </div>
        </div>
        <div class="p-3 bg-gray-50 rounded">
          <div class="text-sm text-gray-600">Total Area</div>
          <div class="text-lg font-semibold">
            {{ formatNumber(stateData.total_area) }} m²
          </div>
        </div>
      </div>
    </div>
    <div v-else class="text-gray-500 text-center">
      Click on a state to view its solar energy details
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SolarState } from '../types'

defineProps<{
  stateData: SolarState | null
}>()

const formatNumber = (value: number): string => {
  return value ? value.toLocaleString(undefined, { 
    maximumFractionDigits: 2 
  }) : '0'
}
</script>