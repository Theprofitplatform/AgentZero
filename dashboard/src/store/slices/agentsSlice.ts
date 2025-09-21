import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Agent } from '../../types';
import { apiService } from '../../services/api';

interface AgentsState {
  agents: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
}

const initialState: AgentsState = {
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchAgents = createAsyncThunk(
  'agents/fetchAgents',
  async () => {
    const agents = await apiService.getAgents();
    return agents;
  }
);

export const fetchAgent = createAsyncThunk(
  'agents/fetchAgent',
  async (id: string) => {
    const agent = await apiService.getAgent(id);
    return agent;
  }
);

export const controlAgent = createAsyncThunk(
  'agents/controlAgent',
  async ({ id, action }: { id: string; action: string }) => {
    await apiService.controlAgent(id, action);
    return { id, action };
  }
);

// Slice
const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    updateAgent: (state, action: PayloadAction<Agent>) => {
      const index = state.agents.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = action.payload;
      } else {
        state.agents.push(action.payload);
      }

      if (state.selectedAgent?.id === action.payload.id) {
        state.selectedAgent = action.payload;
      }
    },
    updateAgentStatus: (state, action: PayloadAction<{ id: string; status: Agent['status'] }>) => {
      const agent = state.agents.find(a => a.id === action.payload.id);
      if (agent) {
        agent.status = action.payload.status;
      }
      if (state.selectedAgent?.id === action.payload.id) {
        state.selectedAgent.status = action.payload.status;
      }
    },
    setSelectedAgent: (state, action: PayloadAction<Agent | null>) => {
      state.selectedAgent = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    removeAgent: (state, action: PayloadAction<string>) => {
      state.agents = state.agents.filter(a => a.id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    // Fetch agents
    builder.addCase(fetchAgents.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchAgents.fulfilled, (state, action) => {
      state.loading = false;
      state.agents = action.payload;
    });
    builder.addCase(fetchAgents.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch agents';
    });

    // Fetch single agent
    builder.addCase(fetchAgent.fulfilled, (state, action) => {
      state.selectedAgent = action.payload;
      const index = state.agents.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = action.payload;
      }
    });

    // Control agent
    builder.addCase(controlAgent.fulfilled, (state, action) => {
      // Update agent status based on action
      const agent = state.agents.find(a => a.id === action.payload.id);
      if (agent) {
        switch (action.payload.action) {
          case 'pause':
            agent.status = 'idle';
            break;
          case 'terminate':
            agent.status = 'terminated';
            break;
          // Add more cases as needed
        }
      }
    });
  },
});

export const { updateAgent, updateAgentStatus, setSelectedAgent, clearError, removeAgent } = agentsSlice.actions;
export default agentsSlice.reducer;