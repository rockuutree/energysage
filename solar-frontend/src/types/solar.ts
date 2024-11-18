// src/types/solar.ts
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

export interface StateStats {
  totalInstallations: number;
  totalCapacity: number;
  averageSize: number;
  yearRange: [number, number];
}

export interface StatsResponse {
  total_installations: number;
  total_capacity_ac: number;
  average_size: number;
  states_count: number;
  year_range: [number, number];
}