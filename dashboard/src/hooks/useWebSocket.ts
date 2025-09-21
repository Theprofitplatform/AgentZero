import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store';
import { websocketService } from '../services/websocket';
import { updateAgent, removeAgent } from '../store/slices/agentsSlice';
import { updateTask } from '../store/slices/tasksSlice';
import { updateMetrics } from '../store/slices/metricsSlice';
import { addNotification, updateConnectionStatus } from '../store/slices/uiSlice';
import { WebSocketMessage } from '../types';

export const useWebSocket = () => {
  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    const handleMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'agent_status':
          if (message.data.agent) {
            dispatch(updateAgent(message.data.agent));
          }
          break;

        case 'agent_registered':
          if (message.data.agent) {
            dispatch(updateAgent(message.data.agent));
            dispatch(addNotification({
              title: 'Agent Registered',
              message: `${message.data.agent.name} has joined the hive`,
              type: 'info',
            }));
          }
          break;

        case 'agent_terminated':
          if (message.data.agent_id) {
            dispatch(removeAgent(message.data.agent_id));
            dispatch(addNotification({
              title: 'Agent Terminated',
              message: `Agent ${message.data.agent_id} has been terminated`,
              type: 'warning',
            }));
          }
          break;

        case 'task_created':
        case 'task_updated':
          if (message.data.task) {
            dispatch(updateTask(message.data.task));
            if (message.type === 'task_created') {
              dispatch(addNotification({
                title: 'New Task Created',
                message: `Task "${message.data.task.name}" has been created`,
                type: 'info',
              }));
            }
          }
          break;

        case 'task_completed':
          if (message.data.task) {
            dispatch(updateTask(message.data.task));
            dispatch(addNotification({
              title: 'Task Completed',
              message: `Task "${message.data.task.name}" has been completed`,
              type: 'success',
            }));
          }
          break;

        case 'task_failed':
          if (message.data.task) {
            dispatch(updateTask(message.data.task));
            dispatch(addNotification({
              title: 'Task Failed',
              message: `Task "${message.data.task.name}" has failed: ${message.data.error}`,
              type: 'error',
            }));
          }
          break;

        case 'metrics_update':
          if (message.data.metrics) {
            dispatch(updateMetrics(message.data.metrics));
          }
          break;

        case 'system_alert':
          dispatch(addNotification({
            title: 'System Alert',
            message: message.data.message || 'System alert received',
            type: message.data.severity || 'warning',
          }));
          break;

        case 'error':
          dispatch(addNotification({
            title: 'Error',
            message: message.data.message || 'An error occurred',
            type: 'error',
          }));
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    };

    const handleConnect = () => {
      dispatch(updateConnectionStatus({ connected: true, reconnecting: false, error: null }));
      dispatch(addNotification({
        title: 'Connected',
        message: 'Connected to AgentZero Hive',
        type: 'success',
      }));
    };

    const handleDisconnect = () => {
      dispatch(updateConnectionStatus({ connected: false, reconnecting: false, error: 'Disconnected from server' }));
      dispatch(addNotification({
        title: 'Disconnected',
        message: 'Lost connection to AgentZero Hive',
        type: 'error',
      }));
    };

    const handleReconnecting = () => {
      dispatch(updateConnectionStatus({ connected: false, reconnecting: true, error: null }));
    };

    const handleError = (error: Error) => {
      dispatch(updateConnectionStatus({ connected: false, reconnecting: false, error: error.message }));
      dispatch(addNotification({
        title: 'Connection Error',
        message: error.message,
        type: 'error',
      }));
    };

    const unsubscribeMessage = websocketService.subscribe('message', handleMessage);
    const unsubscribeConnect = websocketService.subscribe('connect', handleConnect);
    const unsubscribeDisconnect = websocketService.subscribe('disconnect', handleDisconnect);
    const unsubscribeReconnecting = websocketService.subscribe('reconnecting', handleReconnecting);
    const unsubscribeError = websocketService.subscribe('error', handleError);

    websocketService.connect();

    return () => {
      unsubscribeMessage();
      unsubscribeConnect();
      unsubscribeDisconnect();
      unsubscribeReconnecting();
      unsubscribeError();
      websocketService.disconnect();
    };
  }, [dispatch]);

  return websocketService;
};