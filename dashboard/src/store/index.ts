import { configureStore } from '@reduxjs/toolkit';
import agentsReducer from './slices/agentsSlice';
import tasksReducer from './slices/tasksSlice';
import metricsReducer from './slices/metricsSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    agents: agentsReducer,
    tasks: tasksReducer,
    metrics: metricsReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;