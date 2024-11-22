
/**
 * StateInfoPanel Component
 * 
 * A detailed panel component that displays solar installation information for a selected state.
 * Features include summary statistics, searchable installation list, and pagination.
 */
<template>
  <div class="state-info">
  <!-- Header with state name and close button -->
    <div class="header">
      <h2>{{ selectedState }}</h2>
      <button @click="onClose" class="close-btn">&times;</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <p>Loading state data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <!-- Main Data Display -->
    <div v-else-if="stateData?.stats" class="state-data">
      <!-- Stats Grid 2x2-->
      <div class="stats-grid">
        <div class="stat-box">
          <h3>Total Installations</h3>
          <p>{{ stateData.stats.totalInstallations.toLocaleString() }}</p>
        </div>
        <div class="stat-box">
          <h3>Total Capacity</h3>
          <p>{{ formatNumber(stateData.stats.totalCapacity) }} MW</p>
        </div>
        <div class="stat-box">
          <h3>Average Size</h3>
          <p>{{ formatNumber(stateData.stats.averageCapacity) }} MW</p>
        </div>
        <div class="stat-box">
          <h3>Counties</h3>
          <p>{{ stateData.stats.totalCounties }}</p>
        </div>
      </div>

      <hr class="divider" />

      <!-- Installations Section with search and list-->
      <div class="installations-section">
        <div class="list-header">
          <h3>Recent Installations</h3>
          <div class="search-container">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search installations..."
              class="search-input"
            />
          </div>
        </div>
        <!-- No Installations state -->
        <div v-if="!stateData.installations?.length" class="no-data">
          <p>No installations found</p>
        </div>
        <div v-else>
        <!-- No Search Results State -->
          <div v-if="!filteredInstallations.length" class="no-data">
            <p>No matching installations found</p>
          </div>
          <!-- Installation List -->
          <div v-else class="installations-list">
            <div 
              v-for="installation in paginatedInstallations" 
              :key="installation.case_id" 
              class="installation-box"
            >
              <h4>{{ installation.name || 'Unnamed Installation' }}</h4>
              <p>Capacity: {{ formatNumber(installation.capacity_ac) }} MW</p>
              <p>Year: {{ installation.year || 'Unknown' }}</p>
              <p>County: {{ installation.county }}</p>
              <p>Technology: {{ installation.technology || 'Unknown' }}</p>
              <p>Type: {{ installation.axis_type || 'Unknown' }}</p>
              <p v-if="installation.has_battery" class="battery-indicator">
                ⚡️ Includes Battery Storage
              </p>
            </div>

            <!-- Pagination -->
            <div class="pagination">
              <div class="pagination-info">
                Showing {{ startIndex + 1 }}-{{ Math.min(endIndex, filteredInstallations.length) }} 
                of {{ filteredInstallations.length }}
              </div>
              <div class="pagination-controls">
                <button 
                  @click="previousPage" 
                  :disabled="currentPage === 1"
                  class="pagination-button"
                >
                  Previous
                </button>
                <span class="page-number">Page {{ currentPage }} of {{ totalPages }}</span>
                <button 
                  @click="nextPage" 
                  :disabled="currentPage === totalPages"
                  class="pagination-button"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { StateData } from '../types/solar';

/**
 * Component Props Interface
 * @interface Props
 */
interface Props {
  selectedState: string | null; // Selected State Code
  stateData: StateData | null; // State solar installation data
  loading: boolean; // Loading state
  error: string | null; // Error message
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void; // event emitted when panel is closed
}>();

const searchQuery = ref(''); // Installation search query
const currentPage = ref(1); // Current page number
const itemsPerPage = 5; // Number of installations per page


/**
 * Formats a number with one decimal place
 * @param value - Number to format
 * @returns Formatted string or 'N/A' if null/undefined
 */
const formatNumber = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return 'N/A';
  return value.toFixed(1);
};


/**
 * Filtered and sorted installations based on search query
 * Sorts by year (descending) and filters by search term
 */
const filteredInstallations = computed(() => {
  if (!props.stateData?.installations) return [];
  
  const sorted = [...props.stateData.installations]
    .sort((a, b) => (b.year || 0) - (a.year || 0));
  
  if (!searchQuery.value) return sorted;
  
  const query = searchQuery.value.toLowerCase();
  return sorted.filter(installation => {
    return (
      (installation.name?.toLowerCase().includes(query)) ||
      installation.county.toLowerCase().includes(query) ||
      installation.technology?.toLowerCase().includes(query) ||
      installation.axis_type?.toLowerCase().includes(query) ||
      installation.year?.toString().includes(query)
    );
  });
});

/**
 * Pagination computed properties
 */


const totalPages = computed(() => {
  return Math.ceil(filteredInstallations.value.length / itemsPerPage);
});

const startIndex = computed(() => {
  return (currentPage.value - 1) * itemsPerPage;
});

const endIndex = computed(() => {
  return startIndex.value + itemsPerPage;
});

const paginatedInstallations = computed(() => {
  return filteredInstallations.value.slice(startIndex.value, endIndex.value);
});

/**
 * Pagination navigation methods
 */
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};


/**
 * Reset to first page when search query changes
 */
watch(searchQuery, () => {
  currentPage.value = 1;
});

/**
 * Emits close event to parent
 */
const onClose = () => {
  emit('close');
};
</script>

<style scoped>
.state-info {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  font-size: 32px;
  font-weight: bold;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 5px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-box {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.stat-box h3 {
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-box p {
  font-size: 24px;
  margin: 0;
}

/* Divider */
.divider {
  border: 0;
  height: 1px;
  background-color: #e0e0e0;
  margin: 30px 0;
}

/* Installations Section */
.installations-section {
  margin-top: 30px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h3 {
  font-size: 24px;
  font-weight: bold;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  width: 300px;
}

.installations-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.installation-box {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.installation-box h4 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
}

.installation-box p {
  margin: 8px 0;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-button {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  margin: 0 10px;
}

.battery-indicator {
  color: #2c5282;
  margin-top: 10px;
}

.loading {
  text-align: center;
  padding: 20px;
}

.error-message {
  color: #dc3545;
  padding: 15px;
  background: #f8d7da;
  border-radius: 4px;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style>