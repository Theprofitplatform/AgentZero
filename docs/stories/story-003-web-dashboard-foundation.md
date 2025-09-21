# Story 003: Web Dashboard Foundation

## Story Overview
**Epic**: Web Dashboard Development
**Story ID**: STORY-003
**Priority**: P1 (High)
**Estimated Effort**: 13 story points
**Status**: Ready for Development
**Dependencies**: API Enhancement (STORY-004) for full functionality

## User Story
**As a** system user
**I want to** have a web-based dashboard
**So that** I can monitor and control the AgentZero system without using command line

## Acceptance Criteria

### AC1: Dashboard Framework Setup
- [ ] Initialize React or Vue.js project with TypeScript
- [ ] Configure build pipeline (Webpack/Vite)
- [ ] Set up hot module replacement for development
- [ ] Configure ESLint and Prettier
- [ ] Implement responsive layout system
- [ ] Set up routing for main sections

### AC2: Core UI Components
- [ ] Create reusable component library
- [ ] Implement theme system (dark/light mode)
- [ ] Create layout components (Header, Sidebar, Footer)
- [ ] Build data display components (Table, Card, Chart)
- [ ] Implement form components (Input, Select, Button)
- [ ] Add loading and error states

### AC3: Agent Monitoring Interface
- [ ] Display grid/list of all registered agents
- [ ] Show real-time agent status (idle, working, error)
- [ ] Display current task information per agent
- [ ] Show agent capabilities and configuration
- [ ] Implement agent detail view with metrics
- [ ] Add agent control actions (pause, resume, restart)

### AC4: Task Management Interface
- [ ] Create task submission form
- [ ] Display task queue with filtering/sorting
- [ ] Show task execution history
- [ ] Implement task detail view
- [ ] Add task cancellation capability
- [ ] Display task dependencies visualization

### AC5: Real-time Communication
- [ ] Implement WebSocket connection manager
- [ ] Handle connection/reconnection logic
- [ ] Subscribe to real-time events
- [ ] Update UI components on events
- [ ] Implement notification system
- [ ] Add connection status indicator

### AC6: System Metrics Dashboard
- [ ] Create metrics overview page
- [ ] Implement charts for key metrics
- [ ] Add hive efficiency visualization
- [ ] Display system resource usage
- [ ] Show task completion rates
- [ ] Add historical data comparison

## Technical Implementation Details

### Project Structure
```
dashboard/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   └── Modal.tsx
│   │   ├── agents/
│   │   │   ├── AgentCard.tsx
│   │   │   ├── AgentGrid.tsx
│   │   │   ├── AgentDetail.tsx
│   │   │   └── AgentMetrics.tsx
│   │   ├── tasks/
│   │   │   ├── TaskForm.tsx
│   │   │   ├── TaskQueue.tsx
│   │   │   ├── TaskHistory.tsx
│   │   │   └── TaskDetail.tsx
│   │   ├── metrics/
│   │   │   ├── MetricsOverview.tsx
│   │   │   ├── EfficiencyChart.tsx
│   │   │   └── ResourceChart.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── websocket.ts
│   │   └── auth.ts
│   ├── store/
│   │   ├── index.ts
│   │   ├── agents.slice.ts
│   │   ├── tasks.slice.ts
│   │   └── metrics.slice.ts
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useApi.ts
│   │   └── useTheme.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── styles/
│   │   ├── globals.css
│   │   ├── themes.ts
│   │   └── tailwind.config.js
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Agents.tsx
│   │   ├── Tasks.tsx
│   │   ├── Metrics.tsx
│   │   └── Settings.tsx
│   ├── App.tsx
│   └── index.tsx
├── package.json
├── tsconfig.json
├── .eslintrc.js
└── vite.config.ts
```

### Core Components Implementation

```typescript
// src/components/agents/AgentCard.tsx
interface AgentCardProps {
  agent: Agent;
  onAction: (action: AgentAction) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onAction }) => {
  return (
    <Card className="p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold">{agent.name}</h3>
          <p className="text-sm text-gray-500">{agent.agent_id}</p>
        </div>
        <StatusBadge status={agent.status} />
      </div>

      <div className="mt-4">
        <p className="text-sm">Current Task:</p>
        <p className="font-medium">{agent.current_task || "Idle"}</p>
      </div>

      <div className="mt-4 flex gap-2">
        <Button
          size="sm"
          onClick={() => onAction({ type: "pause", agentId: agent.id })}
          disabled={agent.status !== "working"}
        >
          Pause
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onAction({ type: "details", agentId: agent.id })}
        >
          Details
        </Button>
      </div>
    </Card>
  );
};

// src/services/websocket.ts
export class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private eventHandlers = new Map<string, Set<Function>>();

  connect(url: string): void {
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
      this.emit("connected", null);
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.emit(message.type, message.payload);
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.emit("error", error);
    };

    this.socket.onclose = () => {
      console.log("WebSocket disconnected");
      this.emit("disconnected", null);
      this.attemptReconnect();
    };
  }

  subscribe(event: string, handler: Function): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.eventHandlers.get(event)?.delete(handler);
    };
  }

  private emit(event: string, data: any): void {
    this.eventHandlers.get(event)?.forEach(handler => handler(data));
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Reconnect attempt ${this.reconnectAttempts}`);
        this.connect(this.socket?.url || "");
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  send(type: string, payload: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, payload }));
    }
  }
}

// src/hooks/useWebSocket.ts
export const useWebSocket = () => {
  const [connected, setConnected] = useState(false);
  const wsService = useRef(new WebSocketService());

  useEffect(() => {
    const ws = wsService.current;
    ws.connect(process.env.REACT_APP_WS_URL || "ws://localhost:8001");

    const unsubscribe = ws.subscribe("connected", () => setConnected(true));
    const unsubscribe2 = ws.subscribe("disconnected", () => setConnected(false));

    return () => {
      unsubscribe();
      unsubscribe2();
    };
  }, []);

  return {
    connected,
    subscribe: wsService.current.subscribe.bind(wsService.current),
    send: wsService.current.send.bind(wsService.current)
  };
};
```

### State Management (Redux Toolkit)
```typescript
// src/store/agents.slice.ts
interface AgentsState {
  agents: Agent[];
  loading: boolean;
  error: string | null;
  selectedAgent: Agent | null;
}

const agentsSlice = createSlice({
  name: "agents",
  initialState: {
    agents: [],
    loading: false,
    error: null,
    selectedAgent: null
  } as AgentsState,
  reducers: {
    updateAgent: (state, action) => {
      const index = state.agents.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = action.payload;
      }
    },
    setSelectedAgent: (state, action) => {
      state.selectedAgent = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.loading = false;
        state.agents = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || "Failed to fetch agents";
      });
  }
});
```

### Package.json Dependencies
```json
{
  "name": "agentzero-dashboard",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "jest",
    "lint": "eslint src --ext .ts,.tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "@reduxjs/toolkit": "^1.9.5",
    "react-redux": "^8.1.2",
    "axios": "^1.5.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.2.0",
    "vite": "^4.4.0",
    "@vitejs/plugin-react": "^4.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.48.0",
    "@typescript-eslint/eslint-plugin": "^6.5.0",
    "@typescript-eslint/parser": "^6.5.0",
    "jest": "^29.6.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0"
  }
}
```

## Testing Requirements

### Unit Tests
- Test all components in isolation
- Test WebSocket reconnection logic
- Test state management actions
- Test API service methods
- Test utility functions

### Integration Tests
- Test component interaction with state
- Test real-time updates via WebSocket
- Test error handling flows
- Test responsive design breakpoints

### E2E Tests (Cypress)
```javascript
// cypress/e2e/dashboard.cy.js
describe("Dashboard E2E", () => {
  it("displays agents and updates in real-time", () => {
    cy.visit("/");
    cy.get("[data-testid=agent-grid]").should("exist");

    // Simulate WebSocket message
    cy.window().its("wsService").invoke("emit", "agent.status_changed", {
      agentId: "agent-1",
      status: "working"
    });

    cy.get("[data-testid=agent-1-status]").should("contain", "working");
  });

  it("allows task creation", () => {
    cy.visit("/tasks");
    cy.get("[data-testid=create-task-btn]").click();
    cy.get("input[name=taskName]").type("Test Task");
    cy.get("textarea[name=description]").type("Test Description");
    cy.get("button[type=submit]").click();
    cy.get("[data-testid=task-queue]").should("contain", "Test Task");
  });
});
```

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Responsive design works on mobile, tablet, desktop
- [ ] Dark/light theme toggle working
- [ ] WebSocket connection stable with reconnection
- [ ] All components have unit tests
- [ ] Integration tests passing
- [ ] No console errors or warnings
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] Performance: Initial load < 2 seconds
- [ ] Documentation complete

## Implementation Notes

### Development Setup
```bash
# Create dashboard directory
cd /mnt/c/Users/abhis/projects/AgentZero
npx create-vite@latest dashboard --template react-ts
cd dashboard

# Install dependencies
npm install

# Install additional packages
npm install @reduxjs/toolkit react-redux axios chart.js react-chartjs-2
npm install -D tailwindcss autoprefixer postcss

# Initialize Tailwind
npx tailwindcss init -p

# Start development server
npm run dev
```

### Environment Variables
```env
# .env.development
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8001

# .env.production
VITE_API_URL=https://api.agentzero.com/v1
VITE_WS_URL=wss://api.agentzero.com/ws
```

### Performance Optimization
- Implement code splitting for routes
- Use React.lazy for component lazy loading
- Implement virtual scrolling for large lists
- Use memoization for expensive computations
- Optimize bundle size with tree shaking

## Related Documents
- PRD: `/docs/prd.md#FR-3`
- Architecture: `/docs/architecture.md#2.3`
- API Story: STORY-004 (dependency for full functionality)

## Post-Implementation Tasks
- Add advanced data visualizations (D3.js)
- Implement dashboard customization
- Add export functionality (PDF, CSV)
- Create mobile app version (React Native)
- Add keyboard shortcuts for power users

---
**Created**: 2025-09-21
**Last Updated**: 2025-09-21
**Author**: BMad Workflow System