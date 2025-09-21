import React from 'react';
import { Task } from '../../types';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onAction: (taskId: string, action: 'cancel' | 'retry' | 'details') => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onAction }) => {
  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 dark:text-red-400';
      case 'normal':
        return 'text-blue-600 dark:text-blue-400';
      case 'low':
        return 'text-gray-600 dark:text-gray-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 dark:text-white">{task.name}</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">{task.description}</p>
        </div>
        <span
          className={clsx(
            'px-2 py-1 text-xs font-medium rounded-full',
            getStatusColor(task.status)
          )}
        >
          {task.status}
        </span>
      </div>

      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-4 text-sm">
          <span className={clsx('font-medium', getPriorityColor(task.priority))}>
            {task.priority.toUpperCase()}
          </span>
          {task.assigned_to && (
            <span className="text-gray-600 dark:text-gray-400">
              Agent: {task.assigned_to}
            </span>
          )}
        </div>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {formatDistanceToNow(new Date(task.created_at), { addSuffix: true })}
        </span>
      </div>

      {task.status === 'running' && task.progress !== undefined && (
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
            <span>Progress</span>
            <span>{task.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${task.progress}%` }}
            />
          </div>
        </div>
      )}

      {task.tags && task.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {task.tags.map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {task.error && task.status === 'failed' && (
        <div className="mb-3 p-2 bg-red-50 dark:bg-red-900/20 rounded">
          <p className="text-sm text-red-600 dark:text-red-400">
            Error: {task.error}
          </p>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => onAction(task.id, 'details')}
          className="flex-1 px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          Details
        </button>
        {task.status === 'running' && (
          <button
            onClick={() => onAction(task.id, 'cancel')}
            className="flex-1 px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Cancel
          </button>
        )}
        {task.status === 'failed' && (
          <button
            onClick={() => onAction(task.id, 'retry')}
            className="flex-1 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
};