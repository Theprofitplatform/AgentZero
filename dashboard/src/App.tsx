import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider, useSelector } from 'react-redux';
import { store, RootState } from './store';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { AgentGrid } from './components/agents/AgentGrid';
import { TaskQueue } from './components/tasks/TaskQueue';
import { MetricsOverview } from './components/metrics/MetricsOverview';
import { useWebSocket } from './hooks/useWebSocket';
import { clsx } from 'clsx';

const AppContent: React.FC = () => {
  const { activeView, theme, sidebarCollapsed } = useSelector((state: RootState) => state.ui);
  useWebSocket();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return <Dashboard />;
      case 'agents':
        return <AgentGrid />;
      case 'tasks':
        return <TaskQueue />;
      case 'metrics':
        return <MetricsOverview />;
      case 'logs':
        return (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500 dark:text-gray-400">Logs view coming soon...</p>
          </div>
        );
      case 'settings':
        return (
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500 dark:text-gray-400">Settings view coming soon...</p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className={clsx(
          'flex-1 p-6 transition-all duration-300',
          sidebarCollapsed ? 'ml-0' : 'ml-0'
        )}>
          <div className="max-w-7xl mx-auto">
            {renderView()}
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/" element={<AppContent />} />
          <Route path="/agents/:id" element={<AppContent />} />
          <Route path="/tasks/:id" element={<AppContent />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </Provider>
  );
}

export default App
