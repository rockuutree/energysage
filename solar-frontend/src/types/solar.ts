// src/types/solar.ts
/**
 * Types and interfaces for solar installation data structures
 * These types define the shape of data used throughout the application
 */

/**
 * Represents a single solar installation's complete data
 * @interface SolarInstallation
 * @property {number} case_id - Unique identifier for the installation
 * @property {string} state - Two-letter state code where installation is located
 * @property {string} county - County name where installation is located
 * @property {number} latitude - Geographical latitude coordinate
 * @property {number} longitude - Geographical longitude coordinate
 * @property {string | null} name - Name of the installation (if available)
 * @property {number | null} year - Year the installation was completed
 * @property {number | null} capacity_ac - AC power output capacity in megawatts
 * @property {number | null} capacity_dc - DC power output capacity in megawatts
 * @property {string | null} technology - Type of solar technology used (e.g., 'PV')
 * @property {string | null} axis_type - Type of mounting system (e.g., 'single-axis', 'fixed')
 * @property {number | null} area - Total area of the installation in square meters
 */
export interface SolarInstallation {
  case_id: number;
  state: string;
  county: string;
  latitude: number;
  longitude: number;
  name: string | null;
  year: number | null;
  capacity_ac: number | null;
  capacity_dc: number | null;
  technology: string | null;
  axis_type: string | null;
  area: number | null;
}


/**
 * Statistics for a specific state's solar installations
 * @interface StateStats
 * @property {number} totalInstallations - Total number of solar installations in the state
 * @property {number} totalCapacity - Total power generation capacity in megawatts
 * @property {number} averageSize - Average size of installations in megawatts
 * @property {[number, number]} yearRange - Range of installation years [earliest, latest]
 */
export interface StateStats {
  totalInstallations: number;
  totalCapacity: number;
  averageSize: number;
  yearRange: [number, number];
}

/**
 * Response format for aggregate statistics across all states
 * @interface StatsResponse
 * @property {number} total_installations - Total number of installations nationwide
 * @property {number} total_capacity_ac - Total AC power capacity nationwide in megawatts
 * @property {number} average_size - Average installation size nationwide in megawatts
 * @property {number} states_count - Number of states with solar installations
 * @property {[number, number]} year_range - Range of installation years nationwide [earliest, latest]
 */
export interface StatsResponse {
  total_installations: number;
  total_capacity_ac: number;
  average_size: number;
  states_count: number;
  year_range: [number, number];
}