<!-- src/components/SolarMap.vue -->
<template>
  <div class="map-container">
    <div ref="mapContainer" class="map"></div>
    <div v-if="selectedState" class="state-info">
      <h2>{{ selectedState }}</h2>
      <div v-if="stateStats.get(selectedState)" class="stats">
        <div class="stat">
          <h3>Total Installations</h3>
          <p>{{ stateStats.get(selectedState)?.totalInstallations }}</p>
        </div>
        <div class="stat">
          <h3>Total Capacity (MW)</h3>
          <p>{{ (stateStats.get(selectedState)?.totalCapacity || 0).toFixed(1) }}</p>
        </div>
        <div class="stat">
          <h3>Average Size (MW)</h3>
          <p>{{ (stateStats.get(selectedState)?.averageSize || 0).toFixed(1) }}</p>
        </div>
      </div>
      <div v-if="loading" class="loading">Loading...</div>
      <div class="installations-list">
        <h3>Installations</h3>
        <div v-for="installation in installations" :key="installation.case_id" class="installation-item">
          <h4>{{ installation.name || 'Unnamed Installation' }}</h4>
          <p>Capacity: {{ installation.capacity_ac }} MW</p>
          <p>Year: {{ installation.year }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import maplibregl from 'maplibre-gl';
import { useSolarStore } from '../stores/solar';
import { storeToRefs } from 'pinia';
import 'maplibre-gl/dist/maplibre-gl.css';

const mapContainer = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);
const store = useSolarStore();
const { selectedState, installations, stateStats, loading } = storeToRefs(store);

// Initialize map
onMounted(() => {
  if (!mapContainer.value) return;

  map.value = new maplibregl.Map({
    container: mapContainer.value,
    style: 'https://api.maptiler.com/maps/basic/style.json?key=iGYCn4KVCQlB58GwTz4O', // Get a free key from MapTiler
    center: [-98.5795, 39.8283], // Center of US
    zoom: 3
  });

  map.value.on('load', () => {
    // Add state boundaries layer
    map.value?.addSource('states', {
      type: 'geojson',
      data: 'https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_1_states_provinces_shp.geojson'
    });

    map.value?.addLayer({
      id: 'state-fills',
      type: 'fill',
      source: 'states',
      layout: {},
      paint: {
        'fill-color': '#627BC1',
        'fill-opacity': [
          'case',
          ['boolean', ['==', ['get', 'name'], selectedState.value], false],
          0.7,
          0.3
        ]
      }
    });

    // Add click handler
    map.value?.on('click', 'state-fills', (e) => {
      if (e.features?.[0].properties) {
        const stateName = e.features[0].properties.name;
        store.setSelectedState(stateName);
      }
    });
  });
});

// Update map when selected state changes
watch(selectedState, (newState) => {
  if (!map.value) return;

  map.value.setPaintProperty('state-fills', 'fill-opacity', [
    'case',
    ['boolean', ['==', ['get', 'name'], newState], false],
    0.7,
    0.3
  ]);
});
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
}

.map {
  width: 70%;
  height: 100%;
}

.state-info {
  width: 30%;
  padding: 20px;
  background: white;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.stat {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat h3 {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
}

.stat p {
  font-size: 1.2em;
  font-weight: bold;
  color: #333;
}

.installations-list {
  margin-top: 20px;
}

.installation-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style>