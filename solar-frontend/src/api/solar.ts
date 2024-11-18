// src/api/solar.ts
import axios from 'axios';
import type { InstallationsResponse, Stats } from '../types/solar';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

export const getInstallations = async (params: {
  state?: string;
  year?: number;
  limit?: number;
  offset?: number;
}) => {
  const response = await api.get<InstallationsResponse>('/installations', { params });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get<Stats>('/stats');
  return response.data;
};

export const getStates = async () => {
  const response = await api.get<{ states: string[] }>('/states');
  return response.data.states;
};