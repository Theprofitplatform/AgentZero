import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { MetricsChart } from '../components/metrics/MetricsChart';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';

export const Dashboard: React.FC = () => {
  const { agents } = useSelector((state: RootState) => state.agents);
  const { tasks } = useSelector((state: RootState) => state.tasks);
  const { current: metrics } = useSelector((state: RootState) => state.metrics);
  const { notifications } = useSelector((state: RootState) => state.ui);

  const activeAgents = agents.filter(a => a.status === 'working' || a.status === 'thinking');
  const runningTasks = tasks.filter(t => t.status === 'running');
  const recentNotifications = notifications.slice(0, 5);

  const quickStatsData = {
    labels: ['Active', 'Idle', 'Error'],
    datasets: [{
      label: 'Agents',
      data: [
        agents.filter(a => a.status === 'working' || a.status === 'thinking').length,
        agents.filter(a => a.status === 'idle').length,
        agents.filter(a => a.status === 'error').length,
      ],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(156, 163, 175, 0.8)',
        'rgba(239, 68, 68, 0.8)',
      ],
    }],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard Overview</h1>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          Last updated: {new Date().toLocaleTimeString()}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-4 rounded-lg shadow-md text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Agents</p>
              <p className="text-3xl font-bold">{agents.length}</p>
            </div>
            <svg className="w-12 h-12 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <p className="text-sm text-blue-100 mt-2">
            {activeAgents.length} active
          </p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 p-4 rounded-lg shadow-md text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Tasks Completed</p>
              <p className="text-3xl font-bold">{tasks.filter(t => t.status === 'completed').length}</p>
            </div>
            <svg className="w-12 h-12 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-sm text-green-100 mt-2">
            {runningTasks.length} running
          </p>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-4 rounded-lg shadow-md text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Success Rate</p>
              <p className="text-3xl font-bold">
                {metrics ? `${(metrics.task_stats.success_rate * 100).toFixed(0)}%` : '0%'}
              </p>
            </div>
            <svg className="w-12 h-12 text-purple-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <p className="text-sm text-purple-100 mt-2">
            {metrics?.task_stats.total || 0} total tasks
          </p>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-4 rounded-lg shadow-md text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">System Load</p>
              <p className="text-3xl font-bold">
                {metrics ? `${metrics.cpu_usage.toFixed(0)}%` : '0%'}
              </p>
            </div>
            <svg className="w-12 h-12 text-orange-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <p className="text-sm text-orange-100 mt-2">
            {metrics ? `${(metrics.memory_usage / (1024 * 1024 * 1024)).toFixed(1)}GB` : '0GB'} RAM
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Active Agents</h2>
            {activeAgents.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">No active agents</p>
            ) : (
              <div className="space-y-3">
                {activeAgents.slice(0, 5).map(agent => (
                  <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className={clsx(
                        'w-2 h-2 rounded-full',
                        agent.status === 'working' ? 'bg-green-500' : 'bg-blue-500'
                      )} />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{agent.name}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{agent.current_task || 'No task'}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600 dark:text-gray-400">CPU: {agent.cpu_usage.toFixed(0)}%</p>
                      <p className="text-xs text-gray-500 dark:text-gray-500">
                        {formatDistanceToNow(new Date(agent.last_heartbeat), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Agent Distribution</h2>
            <MetricsChart
              type="doughnut"
              data={quickStatsData}
              title=""
              height={200}
            />
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
            {recentNotifications.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-4">No recent activity</p>
            ) : (
              <div className="space-y-2">
                {recentNotifications.map(notification => (
                  <div key={notification.id} className="border-l-4 border-blue-500 pl-3 py-2">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {notification.title}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Running Tasks</h2>
        {runningTasks.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400 text-center py-8">No running tasks</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Task</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Agent</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Progress</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Started</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {runningTasks.slice(0, 5).map(task => (
                  <tr key={task.id}>
                    <td className="px-4 py-2">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{task.name}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{task.type}</p>
                    </td>
                    <td className="px-4 py-2">
                      <p className="text-sm text-gray-900 dark:text-white">{task.assigned_to || 'Unassigned'}</p>
                    </td>
                    <td className="px-4 py-2">
                      <div className="w-24">
                        <div className="flex items-center">
                          <span className="text-xs text-gray-600 dark:text-gray-400 mr-2">
                            {task.progress || 0}%
                          </span>
                          <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${task.progress || 0}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-2">
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {task.started_at ? formatDistanceToNow(new Date(task.started_at), { addSuffix: true }) : 'Not started'}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};