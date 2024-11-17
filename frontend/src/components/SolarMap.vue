<template>
  <div class="bg-white rounded-lg shadow-lg p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">Solar Installations Map</h2>
      <select 
        v-model="selectedMetric" 
        class="border rounded px-3 py-1"
      >
        <option value="total_capacity_ac">Total Capacity (AC)</option>
        <option value="installation_count">Installation Count</option>
        <option value="avg_capacity">Average Capacity</option>
      </select>
    </div>

    <div class="relative">
      <div 
        ref="mapContainer" 
        class="w-full h-[600px] bg-gray-50 rounded"
      ></div>

      <!-- Legend -->
      <div class="absolute bottom-4 right-4 bg-white p-3 rounded shadow">
        <h4 class="text-sm font-semibold mb-2">{{ selectedMetric }}</h4>
        <div class="flex items-center gap-2">
          <div class="w-24 h-4 bg-gradient-to-r from-blue-100 to-blue-900"></div>
          <div class="text-xs">
            <div>Min: {{ formatValue(minValue) }}</div>
            <div>Max: {{ formatValue(maxValue) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as d3 from 'd3';
import { api } from '../services/api';

const mapContainer = ref<HTMLElement | null>(null);
const selectedMetric = ref('total_capacity_ac');
const minValue = ref(0);
const maxValue = ref(0);

const formatValue = (value: number) => {
  if (selectedMetric.value === 'total_capacity_ac') {
    return `${(value / 1000).toFixed(1)} GW`;
  }
  return value.toLocaleString();
};

const createMap = async () => {
  if (!mapContainer.value) return;

  try {
    // Fetch data
    const data = await api.getStats();
    
    // Set up dimensions
    const width = mapContainer.value.clientWidth;
    const height = mapContainer.value.clientHeight;

    // Create SVG
    const svg = d3.select(mapContainer.value)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Create projection
    const projection = d3.geoAlbersUsa()
      .fitSize([width, height], { type: 'FeatureCollection', features: [] });

    // Create path generator
    const path = d3.geoPath().projection(projection);

    // Create color scale
    const colorScale = d3.scaleSequential(d3.interpolateBlues)
      .domain([0, d3.max(data, d => d[selectedMetric.value as keyof typeof d] as number) || 0]);

    // Draw states
    // Note: You'll need to load US state geometry data
    // This is a placeholder for the actual map drawing code

  } catch (error) {
    console.error('Error creating map:', error);
  }
};

onMounted(() => {
  createMap();
});

watch(selectedMetric, () => {
  // Clear and redraw map with new metric
  if (mapContainer.value) {
    mapContainer.value.innerHTML = '';
    createMap();
  }
});
</script>