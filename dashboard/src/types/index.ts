// Agent types
export interface Agent {
  id: string;
  agent_id: string;
  name: string;
  type: 'planning' | 'execution' | 'research' | 'code';
  status: 'idle' | 'working' | 'thinking' | 'error' | 'terminated';
  current_task?: string;
  capabilities: string[];
  memory_usage: number;
  cpu_usage: number;
  created_at: string;
  last_active: string;
  last_heartbeat: string;
  registered_at: string;
  last_updated: string;
  metrics: {
    tasks_completed: number;
    tasks_failed: number;
    average_task_time: number;
    success_rate: number;
    uptime: number;
    avg_completion_time: number;
  };
}

// Task types
export interface Task {
  id: string;
  name: string;
  description: string;
  type: 'general' | 'research' | 'code_generation' | 'analysis' | 'planning' | 'execution';
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  priority: 'low' | 'normal' | 'high';
  assigned_agent: string | null;
  assigned_to?: string;
  dependencies: string[];
  created_at: string;
  started_at?: string;
  completed_at?: string;
  updated_at: string;
  result?: any;
  error?: string;
  progress?: number;
  tags?: string[];
  metadata?: Record<string, any>;
}

// System metrics
export interface AgentStats {
  type: string;
  count: number;
  avg_cpu: number;
}

export interface SystemMetrics {
  total_agents: number;
  active_agents: number;
  tasks_in_queue: number;
  tasks_completed_today: number;
  average_completion_time: number;
  system_health: 'healthy' | 'degraded' | 'critical';
  cpu_usage: number;
  memory_usage: number;
  memory_available: number;
  hive_efficiency: number;
  uptime: number;
  network_io: {
    bytes_sent: number;
    bytes_received: number;
  };
  queue_depth: number;
  avg_response_time: number;
  errors_count: number;
  agent_stats: AgentStats[];
  task_stats: {
    total: number;
    pending: number;
    running: number;
    completed: number;
    failed: number;
    success_rate: number;
  };
  timestamp: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'agent_status' | 'agent_registered' | 'agent_terminated' | 'task_created' | 'task_updated' | 'task_completed' | 'task_failed' | 'metrics_update' | 'system_alert' | 'error';
  data: any;
  timestamp: string;
}

export interface ConnectionStatus {
  connected: boolean;
  reconnecting: boolean;
  error: string | null;
}

// Action types for agent control
export interface AgentAction {
  type: 'pause' | 'resume' | 'restart' | 'terminate' | 'details';
  agentId: string;
  params?: any;
}

// Notification types
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}