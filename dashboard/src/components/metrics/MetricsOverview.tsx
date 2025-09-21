import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchMetrics } from '../../store/slices/metricsSlice';
import { MetricsChart } from './MetricsChart';
import { clsx } from 'clsx';

export const MetricsOverview: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { current, history, loading } = useSelector((state: RootState) => state.metrics);

  useEffect(() => {
    dispatch(fetchMetrics());
    const interval = setInterval(() => {
      dispatch(fetchMetrics());
    }, 10000);

    return () => clearInterval(interval);
  }, [dispatch]);

  if (loading && !current) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const cpuChartData = {
    labels: history.map(h => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: history.map(h => h.cpu_usage),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const memoryChartData = {
    labels: history.map(h => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Memory Usage (GB)',
        data: history.map(h => h.memory_usage / (1024 * 1024 * 1024)),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const taskStatusData = {
    labels: ['Completed', 'Running', 'Failed', 'Pending'],
    datasets: [
      {
        label: 'Tasks',
        data: [
          current?.task_stats.completed || 0,
          current?.task_stats.running || 0,
          current?.task_stats.failed || 0,
          current?.task_stats.pending || 0,
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(251, 191, 36, 0.8)',
        ],
      },
    ],
  };

  const getHealthColor = (value: number, thresholds: [number, number]) => {
    if (value < thresholds[0]) return 'text-green-600 dark:text-green-400';
    if (value < thresholds[1]) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">CPU Usage</span>
            <span className={clsx('text-2xl font-bold', getHealthColor(current?.cpu_usage || 0, [60, 80]))}>
              {current?.cpu_usage.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={clsx(
                'h-2 rounded-full transition-all',
                current && current.cpu_usage < 60 ? 'bg-green-500' :
                current && current.cpu_usage < 80 ? 'bg-yellow-500' : 'bg-red-500'
              )}
              style={{ width: `${current?.cpu_usage || 0}%` }}
            />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Memory</span>
            <span className={clsx('text-2xl font-bold', getHealthColor(current?.memory_usage || 0, [8, 12]))}>
              {((current?.memory_usage || 0) / (1024 * 1024 * 1024)).toFixed(1)}GB
            </span>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Available: {((current?.memory_available || 0) / (1024 * 1024 * 1024)).toFixed(1)}GB
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Active Agents</span>
            <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {current?.active_agents || 0}
            </span>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Total: {current?.total_agents || 0}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Success Rate</span>
            <span className={clsx('text-2xl font-bold',
              getHealthColor(100 - (current?.task_stats.success_rate || 0) * 100, [10, 30]))}>
              {((current?.task_stats.success_rate || 0) * 100).toFixed(0)}%
            </span>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {current?.task_stats.completed || 0} / {current?.task_stats.total || 0} tasks
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsChart
          type="line"
          data={cpuChartData}
          title="CPU Usage Over Time"
          height={300}
        />
        <MetricsChart
          type="line"
          data={memoryChartData}
          title="Memory Usage Over Time"
          height={300}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <MetricsChart
          type="doughnut"
          data={taskStatusData}
          title="Task Distribution"
          height={300}
        />

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Uptime</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {Math.floor((current?.uptime || 0) / 3600)}h {Math.floor(((current?.uptime || 0) % 3600) / 60)}m
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Network I/O</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                ↓ {((current?.network_io.bytes_received || 0) / (1024 * 1024)).toFixed(1)}MB
                ↑ {((current?.network_io.bytes_sent || 0) / (1024 * 1024)).toFixed(1)}MB
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Queue Depth</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {current?.queue_depth || 0} tasks
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Avg Response</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {current?.avg_response_time.toFixed(0)}ms
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Agent Performance</h3>
          <div className="space-y-3">
            {current?.agent_stats.map((agent, index) => (
              <div key={index} className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-400">{agent.type}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {agent.count} active
                  </span>
                  <span className={clsx(
                    'text-xs px-2 py-1 rounded-full',
                    agent.avg_cpu < 60 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    agent.avg_cpu < 80 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                    'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  )}>
                    {agent.avg_cpu.toFixed(0)}% CPU
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};