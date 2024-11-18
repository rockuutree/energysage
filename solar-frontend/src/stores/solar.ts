// src/stores/solar.ts
import { defineStore } from 'pinia';
import axios from 'axios';
import type { SolarInstallation, StateStats, StatsResponse } from '../types/solar';

const API_BASE = 'http://localhost:8000';

export const useSolarStore = defineStore('solar', {
  state: () => ({
    installations: [] as SolarInstallation[],
    selectedState: null as string | null,
    stateStats: new Map<string, StateStats>(),
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchInstallations(state?: string) {
      this.loading = true;
      try {
        const params = state ? { state } : {};
        const response = await axios.get(`${API_BASE}/installations`, { params });
        this.installations = response.data.installations;
      } catch (error) {
        this.error = 'Failed to fetch installations';
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async fetchStateStats(state: string) {
      if (this.stateStats.has(state)) return;

      try {
        const response = await axios.get<StatsResponse>(`${API_BASE}/installations`, {
          params: { state }
        });
        
        this.stateStats.set(state, {
          totalInstallations: response.data.installations.length,
          totalCapacity: response.data.installations.reduce((sum, inst) => 
            sum + (inst.capacity_ac || 0), 0),
          averageSize: response.data.installations.reduce((sum, inst) => 
            sum + (inst.capacity_ac || 0), 0) / response.data.installations.length,
          yearRange: [
            Math.min(...response.data.installations.map(i => i.year || 0)),
            Math.max(...response.data.installations.map(i => i.year || 0))
          ]
        });
      } catch (error) {
        console.error(`Failed to fetch stats for ${state}:`, error);
      }
    },

    setSelectedState(state: string | null) {
      this.selectedState = state;
      if (state) {
        this.fetchInstallations(state);
        this.fetchStateStats(state);
      }
    }
  }
});