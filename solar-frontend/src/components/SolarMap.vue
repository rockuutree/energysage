<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import maplibregl from 'maplibre-gl';
import { useSolarStore } from '../stores/solar';
import { storeToRefs } from 'pinia';
import 'maplibre-gl/dist/maplibre-gl.css';

const MAPTILER_KEY = 'iGYCn4KVCQlB58GwTz4O'; // Replace with your key

const mapContainer = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);
const store = useSolarStore();
const { selectedState, stateData, loading, error, allStates } = storeToRefs(store);

// Format numbers for display
const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return 'N/A';
  return value.toFixed(1);
};

// Get top 5 states by capacity
const topStates = computed(() => {
  return [...allStates.value]
    .sort((a, b) => b.totalCapacity - a.totalCapacity)
    .slice(0, 5);
});

// Sort installations by year, most recent first
const sortedInstallations = computed(() => {
  if (!stateData.value?.installations) return [];
  return [...stateData.value.installations]
    .sort((a, b) => (b.year || 0) - (a.year || 0));
});

onMounted(async () => {
  await store.fetchStates();

  if (!mapContainer.value) return;

  map.value = new maplibregl.Map({
    container: mapContainer.value,
    style: `https://api.maptiler.com/maps/basic-v2/style.json?key=${MAPTILER_KEY}`,
    center: [-98.5795, 39.8283],
    zoom: 3
  });

  map.value.on('load', () => {
    fetch('https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_110m_admin_1_states_provinces_shp.geojson')
      .then(response => response.json())
      .then(statesData => {
        // Get max capacity for color scaling
        const maxCapacity = Math.max(...allStates.value.map(s => s.totalCapacity));
        
        // Add state capacity data to GeoJSON
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

        map.value?.addSource('states', {
          type: 'geojson',
          data: processedData,
          generateId: true
        });

        // Add the choropleth layer
        map.value?.addLayer({
          id: 'state-fills',
          type: 'fill',
          source: 'states',
          paint: {
            'fill-color': [
              'interpolate',
              ['linear'],
              ['get', 'capacity'],
              0, '#CCCCCC',  // No data
              1, '#FFF9C4',  // Very light yellow
              maxCapacity * 0.25, '#FFEB3B',  // Light yellow
              maxCapacity * 0.5, '#FDD835',   // Medium yellow
              maxCapacity * 0.75, '#FFB300',  // Dark yellow
              maxCapacity, '#FF8F00'          // Orange
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

        // Add state borders
        map.value?.addLayer({
          id: 'state-borders',
          type: 'line',
          source: 'states',
          paint: {
            'line-color': '#627BC1',
            'line-width': 1
          }
        });

        // Add hover effect
        let hoveredStateId: number | null = null;

        // Add legend
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

        // Rest of your event handlers...
        map.value?.on('mousemove', 'state-fills', (e) => {
          if (e.features && e.features.length > 0 && map.value) {
            if (hoveredStateId !== null) {
              map.value.setFeatureState(
                { source: 'states', id: hoveredStateId },
                { hover: false }
              );
            }

            hoveredStateId = e.features[0].id as number;
            if (hoveredStateId !== null) {
              map.value.setFeatureState(
                { source: 'states', id: hoveredStateId },
                { hover: true }
              );
            }

            // Add tooltip
            const feature = e.features[0];
            const capacity = feature.properties.capacity;
            const state = feature.properties.postal;
            
            const tooltip = document.createElement('div');
            tooltip.className = 'map-tooltip';
            tooltip.innerHTML = `
              <strong>${state}</strong><br>
              Capacity: ${formatNumber(capacity)} MW
            `;
            
            const coordinates = e.lngLat;
            
            // Update tooltip position
            const tooltipOffset = 10;
            tooltip.style.left = `${e.point.x + tooltipOffset}px`;
            tooltip.style.top = `${e.point.y + tooltipOffset}px`;
            
            // Remove existing tooltip
            const existingTooltip = document.querySelector('.map-tooltip');
            if (existingTooltip) {
              existingTooltip.remove();
            }
            
            mapContainer.value?.appendChild(tooltip);
            map.value.getCanvas().style.cursor = 'pointer';
          }
        });

        map.value?.on('mouseleave', 'state-fills', () => {
          if (hoveredStateId !== null && map.value) {
            map.value.setFeatureState(
              { source: 'states', id: hoveredStateId },
              { hover: false }
            );
          }
          if (map.value) {
            map.value.getCanvas().style.cursor = '';
          }
          hoveredStateId = null;
          
          // Remove tooltip
          const tooltip = document.querySelector('.map-tooltip');
          if (tooltip) {
            tooltip.remove();
          }
        });

        map.value?.on('click', 'state-fills', (e) => {
          if (e.features && e.features.length > 0) {
            const properties = e.features[0].properties;
            if (properties.postal) {
              store.fetchStateData(properties.postal);
            }
          }
        });
      });
  });
});

// Update map when selected state changes
watch(selectedState, (newState) => {
  if (!map.value) return;

  map.value.setPaintProperty('state-fills', 'fill-color', [
    'case',
    ['==', ['get', 'postal'], newState],
    '#627BC1',
    '#CCCCCC'
  ]);
});
</script>


<!-- src/components/SolarMap.vue -->
<template>
  <div class="map-container">
    <div ref="mapContainer" class="map"></div>
    
    <!-- Empty State -->
    <div v-if="!selectedState" class="state-info">
      <h2>US Solar Installations Map</h2>
      <p>Click on a state to view installation details</p>
      <div v-if="!loading" class="overview">
        <div class="stats-overview">
          <h3>Overview</h3>
          <p><strong>States with Data:</strong> {{ allStates.length }}</p>
          <div class="top-states">
            <h4>Top States by Capacity:</h4>
            <ul>
              <li v-for="state in topStates" :key="state.code">
                {{ state.code }}: {{ formatNumber(state.totalCapacity) }} MW
                ({{ state.installations }} installations)
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- State Information Panel -->
    <div v-else class="state-info">
      <div class="header">
        <h2>{{ selectedState }}</h2>
        <button @click="store.clearSelectedState()" class="close-btn">&times;</button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading">
        <p>Loading state data...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
      </div>

      <!-- Data Display -->
      <div v-else-if="stateData?.stats" class="state-data">
        <div class="stats-grid">
          <div class="stat-card">
            <h3>Total Installations</h3>
            <p>{{ stateData.stats.totalInstallations.toLocaleString() }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Capacity</h3>
            <p>{{ formatNumber(stateData.stats.totalCapacity) }} MW</p>
          </div>
          <div class="stat-card">
            <h3>Average Size</h3>
            <p>{{ formatNumber(stateData.stats.averageCapacity) }} MW</p>
          </div>
          <div class="stat-card">
            <h3>Counties</h3>
            <p>{{ stateData.stats.totalCounties }}</p>
          </div>
        </div>

        <div class="installations-list">
          <h3>Recent Installations</h3>
          <div v-if="!stateData.installations?.length" class="no-data">
            <p>No installations found</p>
          </div>
          <div v-else>
            <div v-for="installation in sortedInstallations" 
                 :key="installation.case_id" 
                 class="installation-item">
              <h4>{{ installation.name || 'Unnamed Installation' }}</h4>
              <div class="installation-details">
                <p>
                  <span class="label">Capacity:</span> 
                  {{ formatNumber(installation.capacity_ac) }} MW
                </p>
                <p>
                  <span class="label">Year:</span> 
                  {{ installation.year || 'Unknown' }}
                </p>
                <p>
                  <span class="label">County:</span> 
                  {{ installation.county }}
                </p>
                <p>
                  <span class="label">Technology:</span> 
                  {{ installation.technology || 'Unknown' }}
                </p>
                <p>
                  <span class="label">Type:</span> 
                  {{ installation.axis_type || 'Unknown' }}
                </p>
                <p v-if="installation.has_battery" class="battery-indicator">
                  ⚡️ Includes Battery Storage
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

\

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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-card h3 {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
}

.stat-card p {
  font-size: 1.2em;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.installations-list {
  margin-top: 20px;
}

.installation-item {
  background: #f8f9fa;
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.installation-item h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.installation-details p {
  margin: 5px 0;
}

.label {
  font-weight: bold;
  color: #666;
  margin-right: 5px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  color: #dc3545;
  padding: 15px;
  background: #f8d7da;
  border-radius: 4px;
  margin-top: 20px;
}

.battery-indicator {
  color: #2c5282;
  font-weight: 500;
  margin-top: 8px;
}

.overview {
  padding: 20px 0;
}

.stats-overview h3 {
  margin-bottom: 15px;
  color: #333;
}

.top-states {
  margin-top: 20px;
}

.top-states h4 {
  color: #666;
  margin-bottom: 10px;
}

.top-states ul {
  list-style: none;
  padding: 0;
}

.top-states li {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 20px;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  z-index: 1;
}

.map-legend h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
}

.legend-scale {
  display: flex;
  flex-direction: column;
  gap: 5px;
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
}

.legend-entry span {
  font-size: 12px;
}

.map-tooltip {
  position: absolute;
  background: white;
  padding: 8px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
  font-size: 12px;
  pointer-events: none;
  z-index: 2;
}
</style>
