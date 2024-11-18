// src/stores/solar.ts
import { defineStore } from 'pinia';
import axios from 'axios';

interface SolarInstallation {
  case_id: number;
  name: string | null;
  county: string;
  latitude: number;
  longitude: number;
  capacity_ac: number | null;
  capacity_dc: number | null;
  year: number | null;
  technology: string | null;
  axis_type: string | null;
  has_battery: boolean;
}

interface StateStats {
  totalInstallations: number;
  totalCapacity: number;
  averageCapacity: number;
  totalCounties: number;
  yearRange: [number, number] | null;
}

interface StateInfo {
  code: string;
  installations: number;
  totalCapacity: number;
}

export const useSolarStore = defineStore('solar', {
  state: () => ({
    selectedState: null as string | null,
    stateData: null as { stats: StateStats; installations: SolarInstallation[] } | null,
    allStates: [] as StateInfo[],
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchStates() {
      try {
        const response = await axios.get('http://localhost:8000/api/states');
        this.allStates = response.data.states;
      } catch (error) {
        console.error('Error fetching states:', error);
        this.error = 'Failed to fetch states';
      }
    },

    async fetchStateData(state: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:8000/api/state/${state}`);
        if (response.data.error) {
          this.error = response.data.error;
          this.stateData = null;
        } else {
          this.stateData = response.data;
          this.selectedState = state;
        }
      } catch (error) {
        console.error(`Failed to fetch data for ${state}:`, error);
        this.error = `Failed to fetch data for ${state}`;
        this.stateData = null;
      } finally {
        this.loading = false;
      }
    },

    clearSelectedState() {
      this.selectedState = null;
      this.stateData = null;
      this.error = null;
    }
  },

  getters: {
    statesSortedByCapacity: (state) => {
      return [...state.allStates].sort((a, b) => b.totalCapacity - a.totalCapacity);
    }
  }
});