import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Task } from '../../types';
import { apiService } from '../../services/api';

interface TasksState {
  tasks: Task[];
  taskHistory: Task[];
  selectedTask: Task | null;
  loading: boolean;
  error: string | null;
}

const initialState: TasksState = {
  tasks: [],
  taskHistory: [],
  selectedTask: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async () => {
    const tasks = await apiService.getTasks();
    return tasks;
  }
);

export const fetchTaskHistory = createAsyncThunk(
  'tasks/fetchTaskHistory',
  async (limit: number = 50) => {
    const history = await apiService.getTaskHistory(limit);
    return history;
  }
);

export const createTask = createAsyncThunk(
  'tasks/createTask',
  async (task: Partial<Task>) => {
    const newTask = await apiService.createTask(task);
    return newTask;
  }
);

export const cancelTask = createAsyncThunk(
  'tasks/cancelTask',
  async (id: string) => {
    await apiService.cancelTask(id);
    return id;
  }
);

// Slice
const tasksSlice = createSlice({
  name: 'tasks',
  initialState,
  reducers: {
    updateTask: (state, action: PayloadAction<Task>) => {
      const index = state.tasks.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.tasks[index] = action.payload;
      } else {
        state.tasks.push(action.payload);
      }

      if (state.selectedTask?.id === action.payload.id) {
        state.selectedTask = action.payload;
      }
    },
    updateTaskStatus: (state, action: PayloadAction<{ id: string; status: Task['status'] }>) => {
      const task = state.tasks.find(t => t.id === action.payload.id);
      if (task) {
        task.status = action.payload.status;

        // Move to history if completed or failed
        if (action.payload.status === 'completed' || action.payload.status === 'failed') {
          state.taskHistory.unshift(task);
          state.tasks = state.tasks.filter(t => t.id !== action.payload.id);
        }
      }
    },
    updateTaskProgress: (state, action: PayloadAction<{ id: string; progress: number }>) => {
      const task = state.tasks.find(t => t.id === action.payload.id);
      if (task) {
        task.progress = action.payload.progress;
      }
      if (state.selectedTask?.id === action.payload.id) {
        state.selectedTask.progress = action.payload.progress;
      }
    },
    setSelectedTask: (state, action: PayloadAction<Task | null>) => {
      state.selectedTask = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch tasks
    builder.addCase(fetchTasks.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchTasks.fulfilled, (state, action) => {
      state.loading = false;
      state.tasks = action.payload;
    });
    builder.addCase(fetchTasks.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch tasks';
    });

    // Fetch task history
    builder.addCase(fetchTaskHistory.fulfilled, (state, action) => {
      state.taskHistory = action.payload;
    });

    // Create task
    builder.addCase(createTask.fulfilled, (state, action) => {
      state.tasks.push(action.payload);
    });

    // Cancel task
    builder.addCase(cancelTask.fulfilled, (state, action) => {
      const task = state.tasks.find(t => t.id === action.payload);
      if (task) {
        task.status = 'cancelled';
      }
    });
  },
});

export const { updateTask, updateTaskStatus, updateTaskProgress, setSelectedTask, clearError } = tasksSlice.actions;
export default tasksSlice.reducer;