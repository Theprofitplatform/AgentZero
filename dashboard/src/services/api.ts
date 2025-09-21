import axios, { AxiosInstance } from 'axios';
import { Agent, Task, SystemMetrics } from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Agent endpoints
  async getAgents(): Promise<Agent[]> {
    return this.client.get('/agents');
  }

  async getAgent(id: string): Promise<Agent> {
    return this.client.get(`/agents/${id}`);
  }

  async controlAgent(id: string, action: string): Promise<any> {
    return this.client.post(`/agents/${id}/control`, { action });
  }

  async getAgentMetrics(id: string): Promise<any> {
    return this.client.get(`/agents/${id}/metrics`);
  }

  // Task endpoints
  async getTasks(): Promise<Task[]> {
    return this.client.get('/tasks');
  }

  async getTask(id: string): Promise<Task> {
    return this.client.get(`/tasks/${id}`);
  }

  async createTask(task: Partial<Task>): Promise<Task> {
    return this.client.post('/tasks', task);
  }

  async cancelTask(id: string): Promise<void> {
    return this.client.post(`/tasks/${id}/cancel`);
  }

  async getTaskHistory(limit = 50): Promise<Task[]> {
    return this.client.get('/tasks/history', { params: { limit } });
  }

  // System metrics
  async getSystemMetrics(): Promise<SystemMetrics> {
    return this.client.get('/metrics/system');
  }

  async getHiveEfficiency(): Promise<any> {
    return this.client.get('/metrics/hive');
  }

  async getResourceUsage(): Promise<any> {
    return this.client.get('/metrics/resources');
  }

  // Settings
  async getSettings(): Promise<any> {
    return this.client.get('/settings');
  }

  async updateSettings(settings: any): Promise<any> {
    return this.client.put('/settings', settings);
  }
}

export const apiService = new ApiService();