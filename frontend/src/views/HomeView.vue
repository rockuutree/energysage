<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">US Solar Energy Map</h1>
    <div v-if="solarStore.loading" class="text-center py-8">
      Loading solar data...
    </div>
    <div v-else-if="solarStore.error" class="text-red-500 text-center py-8">
      {{ solarStore.error }}
    </div>
    <MapContainer v-else />
  </div>
</template>

<script setup lang="ts">
import MapContainer from '../components/MapContainer.vue'
import { useSolarStore } from '../stores/solar'

const solarStore = useSolarStore()
</script>