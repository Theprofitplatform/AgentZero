import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { TaskCard } from './TaskCard';
import { TaskForm } from './TaskForm';
import { RootState, AppDispatch } from '../../store';
import { fetchTasks, updateTask, createTask } from '../../store/slices/tasksSlice';
import { Task } from '../../types';
import { clsx } from 'clsx';

export const TaskQueue: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { tasks, loading, error } = useSelector((state: RootState) => state.tasks);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filter, setFilter] = useState<Task['status'] | 'all'>('all');

  useEffect(() => {
    dispatch(fetchTasks());
    const interval = setInterval(() => {
      dispatch(fetchTasks());
    }, 3000);

    return () => clearInterval(interval);
  }, [dispatch]);

  const handleTaskAction = (taskId: string, action: 'cancel' | 'retry' | 'details') => {
    switch (action) {
      case 'cancel':
        dispatch(updateTask({ id: taskId, status: 'cancelled' } as any));
        break;
      case 'retry':
        dispatch(updateTask({ id: taskId, status: 'pending', error: null } as any));
        break;
      case 'details':
        window.location.href = `/tasks/${taskId}`;
        break;
    }
  };

  const handleCreateTask = (taskData: Partial<Task>) => {
    dispatch(createTask(taskData));
    setShowCreateForm(false);
  };

  const filteredTasks = filter === 'all'
    ? tasks
    : tasks.filter(task => task.status === filter);

  const getTasksByStatus = (status: Task['status']) =>
    tasks.filter(task => task.status === status);

  if (loading && tasks.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 p-4 rounded-lg">
        <p className="font-semibold">Error loading tasks</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <div className="flex space-x-2">
          {(['all', 'pending', 'running', 'completed', 'failed', 'cancelled'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={clsx(
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                filter === status
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              )}
            >
              {status === 'all' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
              <span className="ml-2 text-xs">
                ({status === 'all' ? tasks.length : getTasksByStatus(status as Task['status']).length})
              </span>
            </button>
          ))}
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          + New Task
        </button>
      </div>

      {showCreateForm && (
        <div className="mb-6">
          <TaskForm
            onSubmit={handleCreateTask}
            onCancel={() => setShowCreateForm(false)}
          />
        </div>
      )}

      <div className="space-y-2">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              No {filter !== 'all' ? filter : ''} tasks
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredTasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onAction={handleTaskAction}
              />
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Pending</p>
          <p className="text-2xl font-bold text-yellow-600">{getTasksByStatus('pending').length}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Running</p>
          <p className="text-2xl font-bold text-blue-600">{getTasksByStatus('running').length}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Completed</p>
          <p className="text-2xl font-bold text-green-600">{getTasksByStatus('completed').length}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Failed</p>
          <p className="text-2xl font-bold text-red-600">{getTasksByStatus('failed').length}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">Cancelled</p>
          <p className="text-2xl font-bold text-gray-600">{getTasksByStatus('cancelled').length}</p>
        </div>
      </div>
    </div>
  );
};