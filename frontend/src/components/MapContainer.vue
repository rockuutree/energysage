<template>
  <div class="grid grid-cols-3 gap-6">
    <div class="col-span-2 bg-white p-4 rounded-lg shadow-lg">
      <USMap @stateSelected="handleStateSelect" />
    </div>
    <StateDetails :stateData="solarStore.selectedState" />
  </div>
</template>

<script setup lang="ts">
import { useSolarStore } from '../stores/solar'
import USMap from './USMap.vue'
import StateDetails from './StateDetails.vue'
import type { SolarState } from '../types'

const solarStore = useSolarStore()

const handleStateSelect = (stateData: SolarState) => {
  solarStore.selectState(stateData)
}
</script>