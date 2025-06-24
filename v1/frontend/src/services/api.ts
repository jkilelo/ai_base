import axios from 'axios';
import { HealthStatus, DatabaseHealthStatus, SystemHealthStatus } from '../types';

const API_BASE_URL = 'http://localhost:8001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const healthApi = {
  // Get general health status
  getHealth: async (): Promise<HealthStatus> => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get database health status
  getDatabaseHealth: async (): Promise<DatabaseHealthStatus> => {
    const response = await api.get('/health/database');
    return response.data;
  },

  // Get system health status
  getSystemHealth: async (): Promise<SystemHealthStatus> => {
    const response = await api.get('/health/system');
    return response.data;
  },

  // Get all health endpoints in parallel
  getAllHealth: async () => {
    try {
      const [health, database, system] = await Promise.allSettled([
        healthApi.getHealth(),
        healthApi.getDatabaseHealth(),
        healthApi.getSystemHealth(),
      ]);

      return {
        health: health.status === 'fulfilled' ? health.value : null,
        database: database.status === 'fulfilled' ? database.value : null,
        system: system.status === 'fulfilled' ? system.value : null,
        errors: {
          health: health.status === 'rejected' ? health.reason : null,
          database: database.status === 'rejected' ? database.reason : null,
          system: system.status === 'rejected' ? system.reason : null,
        }
      };
    } catch (error) {
      throw error;
    }
  }
};

export default api;
