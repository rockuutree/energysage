// src/components/SolarMap.vue
<template>
  <div class="map-container">
    <div ref="mapContainer" class="map"></div>
    
    <!-- Empty State -->
    <div v-if="!selectedState" class="sidebar">
      <h2 class="text-2xl font-semibold mb-4">US Solar Installations Map</h2>
      <p class="text-gray-600 mb-4">Click on a state to view installation details</p>
      <div v-if="!loading" class="overview">
        <div class="stats-overview">
          <h3 class="text-xl font-medium mb-4">Overview</h3>
          <p><strong>States with Data:</strong> {{ allStates.length }}</p>
          <div class="top-states mt-6">
            <h4 class="text-lg font-medium mb-3">Top States by Capacity:</h4>
            <ul class="space-y-2">
              <li v-for="state in topStates" :key="state.code"
                  class="p-2 bg-gray-50 rounded-lg">
                {{ state.code }}: {{ formatNumber(state.totalCapacity) }} MW
                <span class="text-gray-600">
                  ({{ state.installations }} installations)
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- State Information Panel -->
    <div v-else class="sidebar">
      <StateInfoPanel
        :selected-state="selectedState"
        :state-data="stateData"
        :loading="loading"
        :error="error"
        @close="store.clearSelectedState()"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import maplibregl from 'maplibre-gl';
import { useSolarStore } from '../stores/solar';
import { storeToRefs } from 'pinia';
import StateInfoPanel from './StateInfoPanel.vue';
import 'maplibre-gl/dist/maplibre-gl.css';

const MAPTILER_KEY = import.meta.env.VITE_MAPTILER_KEY;

// Refs
const mapContainer = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);
const store = useSolarStore();
const { selectedState, stateData, loading, error, allStates } = storeToRefs(store);

// Utility functions
const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return 'N/A';
  return value.toFixed(1);
};

// Computed properties
const topStates = computed(() => {
  return [...allStates.value]
    .sort((a, b) => b.totalCapacity - a.totalCapacity)
    .slice(0, 5);
});

// Map initialization and setup
const initializeMap = () => {
  if (!mapContainer.value) return;

  map.value = new maplibregl.Map({
    container: mapContainer.value,
    style: `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_KEY}`,
    center: [-98.5795, 39.8283],
    zoom: 3
  });

  map.value.on('load', setupMapLayers);
};

// Map layers setup
const setupMapLayers = async () => {
  if (!map.value) return;

  try {
    const response = await fetch('https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_1_states_provinces_shp.geojson');
    const statesData = await response.json();
    
    const maxCapacity = Math.max(...allStates.value.map(s => s.totalCapacity));
    
    // Process GeoJSON data
    const processedData = {
      type: 'FeatureCollection',
      features: statesData.features
        .filter((feature: any) => feature.properties.admin === 'United States of America')
        .map((feature: any, index: number) => {
          const stateData = allStates.value.find(
            s => s.code === feature.properties.postal
          );
          return {
            ...feature,
            id: index,
            properties: {
              ...feature.properties,
              STATE_ID: index,
              capacity: stateData ? stateData.totalCapacity : 0
            }
          };
        })
    };

    // Add source
    map.value.addSource('states', {
      type: 'geojson',
      data: processedData,
      generateId: true
    });

    // Add fill layer
    map.value.addLayer({
      id: 'state-fills',
      type: 'fill',
      source: 'states',
      paint: {
        'fill-color': [
          'interpolate',
          ['linear'],
          ['get', 'capacity'],
          0, '#CCCCCC',
          1, '#FFF9C4',
          maxCapacity * 0.25, '#FFEB3B',
          maxCapacity * 0.5, '#FDD835',
          maxCapacity * 0.75, '#FFB300',
          maxCapacity, '#FF8F00'
        ],
        'fill-opacity': [
          'case',
          ['boolean', ['==', ['get', 'postal'], selectedState.value], false],
          0.9,
          ['boolean', ['==', ['feature-state', 'hover'], true], false],
          0.7,
          0.5
        ]
      }
    });

    // Add borders layer
    map.value.addLayer({
      id: 'state-borders',
      type: 'line',
      source: 'states',
      paint: {
        'line-color': '#627BC1',
        'line-width': 1
      }
    });

    // Add interactivity
    setupMapInteractions();
    addMapLegend(maxCapacity);
  } catch (error) {
    console.error('Error setting up map layers:', error);
  }
};

// Map interactions setup
const setupMapInteractions = () => {
  if (!map.value) return;

  let hoveredStateId: number | null = null;

  map.value.on('mousemove', 'state-fills', (e) => {
    if (!e.features?.length || !map.value) return;

    if (hoveredStateId !== null) {
      map.value.setFeatureState(
        { source: 'states', id: hoveredStateId },
        { hover: false }
      );
    }

    hoveredStateId = e.features[0].id as number;
    map.value.setFeatureState(
      { source: 'states', id: hoveredStateId },
      { hover: true }
    );

    // Add tooltip
    addTooltip(e);
  });

  map.value.on('mouseleave', 'state-fills', () => {
    if (hoveredStateId !== null && map.value) {
      map.value.setFeatureState(
        { source: 'states', id: hoveredStateId },
        { hover: false }
      );
      map.value.getCanvas().style.cursor = '';
    }
    hoveredStateId = null;
    removeTooltip();
  });

  map.value.on('click', 'state-fills', (e) => {
    if (!e.features?.length) return;
    const properties = e.features[0].properties;
    if (properties.postal) {
      store.fetchStateData(properties.postal);
    }
  });
};

// Tooltip handlers
const addTooltip = (e: maplibregl.MapMouseEvent & { features?: maplibregl.MapboxGeoJSONFeature[] }) => {
  if (!e.features?.length || !mapContainer.value) return;

  const feature = e.features[0];
  const capacity = feature.properties.capacity;
  const state = feature.properties.postal;
  
  const tooltip = document.createElement('div');
  tooltip.className = 'map-tooltip';
  tooltip.innerHTML = `
    <strong>${state}</strong><br>
    Capacity: ${formatNumber(capacity)} MW
  `;
  
  const tooltipOffset = 10;
  tooltip.style.left = `${e.point.x + tooltipOffset}px`;
  tooltip.style.top = `${e.point.y + tooltipOffset}px`;
  
  removeTooltip();
  mapContainer.value.appendChild(tooltip);
};

const removeTooltip = () => {
  const tooltip = document.querySelector('.map-tooltip');
  if (tooltip) {
    tooltip.remove();
  }
};

// Legend setup
const addMapLegend = (maxCapacity: number) => {
  if (!mapContainer.value) return;

  const legend = document.createElement('div');
  legend.className = 'map-legend';
  legend.innerHTML = `
    <h4>Solar Capacity (MW)</h4>
    <div class="legend-scale">
      <div class="legend-entry">
        <div class="legend-color" style="background: #CCCCCC"></div>
        <span>No data</span>
      </div>
      <div class="legend-entry">
        <div class="legend-color" style="background: #FFF9C4"></div>
        <span>0 - ${formatNumber(maxCapacity * 0.25)}</span>
      </div>
      <div class="legend-entry">
        <div class="legend-color" style="background: #FFEB3B"></div>
        <span>${formatNumber(maxCapacity * 0.25)} - ${formatNumber(maxCapacity * 0.5)}</span>
      </div>
      <div class="legend-entry">
        <div class="legend-color" style="background: #FDD835"></div>
        <span>${formatNumber(maxCapacity * 0.5)} - ${formatNumber(maxCapacity * 0.75)}</span>
      </div>
      <div class="legend-entry">
        <div class="legend-color" style="background: #FF8F00"></div>
        <span>${formatNumber(maxCapacity * 0.75)} - ${formatNumber(maxCapacity)}</span>
      </div>
    </div>
  `;
  mapContainer.value.appendChild(legend);
};

// Watch for state changes
watch(selectedState, (newState) => {
  if (!map.value) return;

  map.value.setPaintProperty('state-fills', 'fill-opacity', [
    'case',
    ['boolean', ['==', ['get', 'postal'], newState], false],
    0.9,
    ['boolean', ['==', ['feature-state', 'hover'], true], false],
    0.7,
    0.5
  ]);
});

// Initialize on mount
onMounted(async () => {
  await store.fetchStates();
  initializeMap();
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
  flex: 1;
  height: 100%;
}

.sidebar {
  width: 30%;
  min-width: 400px;
  max-width: 500px;
  height: 100%;
  background: white;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  z-index: 1;
  padding: 20px;
}

.overview {
  padding: 20px 0;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: white;
  padding: 12px;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  z-index: 1;
}

.map-legend h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
}

.legend-scale {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-entry {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border: 1px solid rgba(0,0,0,0.1);
  border-radius: 2px;
}

.legend-entry span {
  font-size: 12px;
  color: #666;
}

.map-tooltip {
  position: absolute;
  background: white;
  padding: 8px 12px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  font-size: 12px;
  pointer-events: none;
  z-index: 2;
  min-width: 120px;
}

.top-states ul {
  list-style: none;
  padding: 0;
}

.top-states li {
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #f5f5f5;
  transition: background-color 0.2s;
}

.top-states li:hover {
  background: #eee;
}
</style>