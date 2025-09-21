import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AgentCard } from './AgentCard';
import { RootState, AppDispatch } from '../../store';
import { fetchAgents, controlAgent } from '../../store/slices/agentsSlice';
import { AgentAction } from '../../types';

export const AgentGrid: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { agents, loading, error } = useSelector((state: RootState) => state.agents);

  useEffect(() => {
    dispatch(fetchAgents());
    // Refresh every 5 seconds
    const interval = setInterval(() => {
      dispatch(fetchAgents());
    }, 5000);

    return () => clearInterval(interval);
  }, [dispatch]);

  const handleAgentAction = (action: AgentAction) => {
    if (action.type === 'details') {
      // Navigate to agent details
      window.location.href = `/agents/${action.agentId}`;
    } else {
      dispatch(controlAgent({ id: action.agentId, action: action.type }));
    }
  };

  if (loading && agents.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 p-4 rounded-lg">
        <p className="font-semibold">Error loading agents</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  if (agents.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No agents registered</p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
          Agents will appear here once they register with the Hive
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4" data-testid="agent-grid">
      {agents.map(agent => (
        <AgentCard
          key={agent.id}
          agent={agent}
          onAction={handleAgentAction}
        />
      ))}
    </div>
  );
};