import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SystemMetrics } from '../../types';
import { apiService } from '../../services/api';

interface MetricsState {
  current: SystemMetrics | null;
  history: SystemMetrics[];
  systemMetrics: SystemMetrics | null;
  hiveEfficiency: any;
  resourceUsage: any;
  historicalData: any[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: MetricsState = {
  current: null,
  history: [],
  systemMetrics: null,
  hiveEfficiency: null,
  resourceUsage: null,
  historicalData: [],
  loading: false,
  error: null,
  lastUpdated: null,
};

// Async thunks
export const fetchMetrics = createAsyncThunk(
  'metrics/fetchMetrics',
  async () => {
    const metrics = await apiService.getSystemMetrics();
    return metrics;
  }
);

export const fetchSystemMetrics = createAsyncThunk(
  'metrics/fetchSystemMetrics',
  async () => {
    const metrics = await apiService.getSystemMetrics();
    return metrics;
  }
);

export const fetchHiveEfficiency = createAsyncThunk(
  'metrics/fetchHiveEfficiency',
  async () => {
    const efficiency = await apiService.getHiveEfficiency();
    return efficiency;
  }
);

export const fetchResourceUsage = createAsyncThunk(
  'metrics/fetchResourceUsage',
  async () => {
    const usage = await apiService.getResourceUsage();
    return usage;
  }
);

// Slice
const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<SystemMetrics>) => {
      state.current = action.payload;
      state.history.push(action.payload);
      if (state.history.length > 50) {
        state.history = state.history.slice(-50);
      }
      state.lastUpdated = new Date().toISOString();
    },
    updateSystemMetrics: (state, action: PayloadAction<Partial<SystemMetrics>>) => {
      if (state.systemMetrics) {
        state.systemMetrics = { ...state.systemMetrics, ...action.payload };
      } else {
        state.systemMetrics = action.payload as SystemMetrics;
      }
      state.lastUpdated = new Date().toISOString();
    },
    updateHiveEfficiency: (state, action: PayloadAction<any>) => {
      state.hiveEfficiency = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    updateResourceUsage: (state, action: PayloadAction<any>) => {
      state.resourceUsage = action.payload;
      state.lastUpdated = new Date().toISOString();
    },
    addHistoricalDataPoint: (state, action: PayloadAction<any>) => {
      state.historicalData.push({
        ...action.payload,
        timestamp: new Date().toISOString(),
      });
      // Keep only last 100 data points
      if (state.historicalData.length > 100) {
        state.historicalData = state.historicalData.slice(-100);
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // System metrics
    builder.addCase(fetchSystemMetrics.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchSystemMetrics.fulfilled, (state, action) => {
      state.loading = false;
      state.systemMetrics = action.payload;
      state.lastUpdated = new Date().toISOString();
    });
    builder.addCase(fetchSystemMetrics.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch system metrics';
    });

    // Hive efficiency
    builder.addCase(fetchHiveEfficiency.fulfilled, (state, action) => {
      state.hiveEfficiency = action.payload;
      state.lastUpdated = new Date().toISOString();
    });

    // Resource usage
    builder.addCase(fetchResourceUsage.fulfilled, (state, action) => {
      state.resourceUsage = action.payload;
      state.lastUpdated = new Date().toISOString();
    });
  },
});

export const {
  updateMetrics,
  updateSystemMetrics,
  updateHiveEfficiency,
  updateResourceUsage,
  addHistoricalDataPoint,
  clearError
} = metricsSlice.actions;

export default metricsSlice.reducer;