// src/stores/solar.ts

/**
 * Solar Installations Store
 * This Pinia store manages the state and operations for solar installation data across US states.
 */

import { defineStore } from 'pinia';
// Makes the HTTP request to the API
import axios from 'axios';

// This is a Pinia store that manages the application's state


/**
 * Interface representing a single solar installation
 * @interface SolarInstallation
 * 
 *  */
interface SolarInstallation {
  case_id: number; // Unique identifier for the installation
  name: string | null; // Name of the installation
  county: string; // County where the installation is located
  latitude: number; // Latitude of the installation
  longitude: number; // Longitude of the installation
  capacity_ac: number | null; // capacity_ac - AC power capacity in megawatts
  capacity_dc: number | null; // capacity_dc - DC power capacity in megawatts
  year: number | null; // year - Year the installation was completed
  technology: string | null; // technology - Solar technology used in the installation
  axis_type: string | null; // axis_type - Axis type of the installation
  has_battery: boolean; // has_battery - Indicates if the installation has a battery
}

/**
 * Interface representing aggregate statistics for a state
 * @interface StateStats
 * @property {number} totalInstallations - Total number of installations in the state
 * @property {number} totalCapacity - Total power capacity in megawatts
 * @property {number} averageCapacity - Average installation capacity in megawatts
 * @property {number} totalCounties - Number of counties with installations
 * @property {[number, number] | null} yearRange - Range of installation years [earliest, latest]
 */
interface StateStats {
  totalInstallations: number;
  totalCapacity: number;
  averageCapacity: number;
  totalCounties: number;
  yearRange: [number, number] | null;
}

/**
 * Interface representing basic state information
 * @interface StateInfo
 * @property {string} code - State code (e.g., 'CA', 'NY')
 * @property {number} installations - Number of installations in the state
 * @property {number} totalCapacity - Total power capacity in megawatts
 */
interface StateInfo {
  code: string;
  installations: number;
  totalCapacity: number;
}

/**
 * Solar installations store definition
 * Manages state data and operations for solar installations across US states
 */
export const useSolarStore = defineStore('solar', {
    /**
   * State definition
   * @returns Initial state object
   */
  state: () => ({
    // Currently selected state code
    selectedState: null as string | null,
     // Detailed data for selected state
    stateData: null as { stats: StateStats; installations: SolarInstallation[] } | null,
    // List of all states with basic info
    allStates: [] as StateInfo[],
     // Loading state indicator
    loading: false,
      // Error message storage
    error: null as string | null
  }),



    /**
   * Store actions for data fetching and state management
    actions: {
      /**
       * Fetches basic information for all states
       * Updates allStates array with received data
       */
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

    /**
     * Fetches detailed data for a specific state
     * Updates stateData with received information
     * @param {string} state - State code to fetch data for
     */
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

    /**
     * Clears the selected state and associated data
     * Resets selectedState, stateData, and error to null
     */
    clearSelectedState() {
      this.selectedState = null;
      this.stateData = null;
      this.error = null;
    }
  },

  /**
   * Computed properties (getters)

  getters: {
     * Returns all states sorted by total capacity in descending order
     * @param {Object} state - Store state
     * @returns {StateInfo[]} Sorted array of states
     */
  getters: {
    statesSortedByCapacity: (state) => {
      return [...state.allStates].sort((a, b) => b.totalCapacity - a.totalCapacity);
    }
  }
});