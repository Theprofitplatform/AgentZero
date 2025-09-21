import React from 'react';
import { Agent, AgentAction } from '../../types';
import { clsx } from 'clsx';

interface AgentCardProps {
  agent: Agent;
  onAction: (action: AgentAction) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onAction }) => {
  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'idle':
        return 'bg-gray-500';
      case 'working':
        return 'bg-green-500';
      case 'thinking':
        return 'bg-blue-500';
      case 'error':
        return 'bg-red-500';
      case 'terminated':
        return 'bg-gray-700';
      default:
        return 'bg-gray-500';
    }
  };

  const getAgentIcon = (type: Agent['type']) => {
    switch (type) {
      case 'planning':
        return '📋';
      case 'execution':
        return '⚙️';
      case 'research':
        return '🔍';
      case 'code':
        return '💻';
      default:
        return '🤖';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">{getAgentIcon(agent.type)}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {agent.name}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">{agent.agent_id}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={clsx(
              'w-2 h-2 rounded-full animate-pulse',
              getStatusColor(agent.status)
            )}
          />
          <span className="text-sm text-gray-600 dark:text-gray-300 capitalize">
            {agent.status}
          </span>
        </div>
      </div>

      {agent.current_task && (
        <div className="mb-3 p-2 bg-gray-50 dark:bg-gray-700 rounded">
          <p className="text-sm text-gray-600 dark:text-gray-300">Current Task:</p>
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {agent.current_task}
          </p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
          <p className="text-xs text-gray-500 dark:text-gray-400">CPU</p>
          <p className="text-sm font-semibold text-gray-900 dark:text-white">
            {agent.cpu_usage.toFixed(1)}%
          </p>
        </div>
        <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
          <p className="text-xs text-gray-500 dark:text-gray-400">Memory</p>
          <p className="text-sm font-semibold text-gray-900 dark:text-white">
            {agent.memory_usage.toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="flex justify-between items-center mb-3">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          <p>Tasks: {agent.metrics.tasks_completed} completed</p>
          <p>Success: {(agent.metrics.success_rate * 100).toFixed(0)}%</p>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => onAction({ type: 'details', agentId: agent.id })}
          className="flex-1 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Details
        </button>
        {agent.status === 'working' && (
          <button
            onClick={() => onAction({ type: 'pause', agentId: agent.id })}
            className="flex-1 px-3 py-1 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600 transition-colors"
          >
            Pause
          </button>
        )}
        {agent.status === 'idle' && (
          <button
            onClick={() => onAction({ type: 'resume', agentId: agent.id })}
            className="flex-1 px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
          >
            Resume
          </button>
        )}
        {agent.status === 'error' && (
          <button
            onClick={() => onAction({ type: 'restart', agentId: agent.id })}
            className="flex-1 px-3 py-1 text-sm bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
          >
            Restart
          </button>
        )}
      </div>
    </div>
  );
};