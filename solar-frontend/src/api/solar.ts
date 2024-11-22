// src/api/solar.ts
// This file handles the api communication layer for the solar data. It exports two functions: getStateData and getAllStates. 


import axios from 'axios';
import type { StateStats, SolarInstallation, StateInfo } from '../types/solar';


/**
 * Configured axios instance for API requests
 * Base URL is set to the solar data API endpoint
 */
const api = axios.create({
  baseURL: 'http://localhost:8000/api'
});

/**
 * Interface for the response when fetching individual state data
 * @interface StateResponse
 * @property {StateStats} stats - Aggregate statistics for the state
 * @property {SolarInstallation[]} installations - Array of individual installations in the state
 */
interface StateResponse {
  stats: StateStats;
  installations: SolarInstallation[];
}

/**
 * Interface for the response when fetching all states data
 * @interface StatesResponse
 * @property {StateInfo[]} states - Array of basic information for all states
 */
interface StatesResponse {
  states: StateInfo[];
}

/**
 * Fetches detailed solar installation data for a specific state
 * 
 * @async
 * @function getStateData
 * @param {string} state - Two-letter state code (e.g., 'CA', 'NY')
 * @returns {Promise<StateResponse>} Promise resolving to state statistics and installation details
 * @throws Will throw an error if the API request fails
 * 
 * @example
 * ```typescript
 * const californiaData = await getStateData('CA');
 * console.log(californiaData.stats.totalInstallations);
 * ```
 */
export const getStateData = async (state: string): Promise<StateResponse> => {
  const response = await api.get<StateResponse>(`/state/${state}`);
  return response.data;
};

/**
 * Fetches basic information for all states with solar installations
 * 
 * @async
 * @function getAllStates
 * @returns {Promise<StatesResponse>} Promise resolving to array of state information
 * @throws Will throw an error if the API request fails
 * 
 * @example
 * ```typescript
 * const allStates = await getAllStates();
 * console.log(allStates.states.length, 'states have solar installations');
 * ```
 */
export const getAllStates = async (): Promise<StatesResponse> => {
  const response = await api.get<StatesResponse>('/states');
  return response.data;
};