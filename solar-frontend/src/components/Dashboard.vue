<!-- src/components/Dashboard.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getInstallations, getStats, getStates } from '../api/solar';
import type { SolarInstallation, Stats } from '../types/solar';
import 'leaflet/dist/leaflet.css';

const installations = ref<SolarInstallation[]>([]);
const stats = ref<Stats | null>(null);
const states = ref<string[]>([]);
const selectedState = ref<string>('');
const loading = ref(true);

onMounted(async () => {
  try {
    const [installationsData, statsData, statesData] = await Promise.all([
      getInstallations({ limit: 50 }),
      getStats(),
      getStates()
    ]);

    installations.value = installationsData.installations;
    stats.value = statsData;
    states.value = statesData;
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
});

const filterByState = async (state: string) => {
  loading.value = true;
  try {
    const response = await getInstallations({ state, limit: 50 });
    installations.value = response.installations;
  } catch (error) {
    console.error('Error filtering data:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="dashboard">
    <div v-if="loading">Loading...</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card" v-if="stats">
          <h3>Total Installations</h3>
          <p>{{ stats.total_installations.toLocaleString() }}</p>
        </div>
        <div class="stat-card" v-if="stats">
          <h3>Total Capacity (AC)</h3>
          <p>{{ stats.total_capacity_ac.toLocaleString() }} MW</p>
        </div>
        <div class="stat-card" v-if="stats">
          <h3>Average Size</h3>
          <p>{{ stats.average_size.toFixed(1) }} MW</p>
        </div>
        <div class="stat-card" v-if="stats">
          <h3>States Covered</h3>
          <p>{{ stats.states_count }}</p>
        </div>
      </div>

      <div class="filters">
        <select v-model="selectedState" @change="filterByState(selectedState)">
          <option value="">All States</option>
          <option v-for="state in states" :key="state" :value="state">
            {{ state }}
          </option>
        </select>
      </div>

      <div class="installations-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>State</th>
              <th>Year</th>
              <th>Capacity (AC)</th>
              <th>Technology</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="installation in installations" :key="installation.case_id">
              <td>{{ installation.name || 'N/A' }}</td>
              <td>{{ installation.state }}</td>
              <td>{{ installation.year }}</td>
              <td>{{ installation.capacity_ac?.toFixed(1) }} MW</td>
              <td>{{ installation.technology }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filters {
  margin-bottom: 20px;
}

.installations-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
}
</style>