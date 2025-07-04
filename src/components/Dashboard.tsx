import React, { useState, useEffect } from 'react';
import { Play, Square, Download, FileText, AlertCircle, CheckCircle, Clock, Wifi } from 'lucide-react';

interface SystemStatus {
  is_running: boolean;
  scheduler_status: {
    is_running: boolean;
    current_execution: unknown;
    next_run: string | null;
    scheduled_jobs: number;
  };
  directories: {
    data: string;
    logs: string;
    downloads: string;
  };
  configuration: {
    wifi_url: string;
    vbs_primary_path: string;
    schedules: Record<string, unknown>;
  };
}

interface LogEntry {
  timestamp: string;
  level: string;
  component: string;
  message: string;
}

const Dashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = 'http://localhost:5000';

  useEffect(() => {
    fetchSystemStatus();
    fetchLogs();
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchLogs();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/api/status`);
      if (response.ok) {
        const data: SystemStatus = await response.json();
        setSystemStatus(data);
        setError(null);
      } else {
        setError('Failed to fetch system status');
      }
    } catch (err) {
      setError('Backend not accessible. Please ensure the API server is running.');
      console.error('Status fetch error:', err);
    }
  };

  const fetchLogs = async (): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/api/logs`);
      if (response.ok) {
        const data: { logs: LogEntry[] } = await response.json();
        setLogs(data.logs || []);
      }
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    }
  };

  const handleStartSystem = async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/start`, { method: 'POST' });
      if (response.ok) {
        await fetchSystemStatus();
        setError(null);
      } else {
        setError('Failed to start system');
      }
    } catch (err) {
      setError('Failed to start system');
      console.error('Start system error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStopSystem = async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/stop`, { method: 'POST' });
      if (response.ok) {
        await fetchSystemStatus();
        setError(null);
      } else {
        setError('Failed to stop system');
      }
    } catch (err) {
      setError('Failed to stop system');
      console.error('Stop system error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleManualExecution = async (taskType: string, slotNumber?: number): Promise<void> => {
    setLoading(true);
    try {
      const body = slotNumber ? { slot_number: slotNumber } : {};
      const response = await fetch(`${API_BASE}/api/execute/${taskType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (response.ok) {
        await fetchSystemStatus();
        setError(null);
      } else {
        setError(`Failed to execute ${taskType}`);
      }
    } catch (err) {
      setError(`Failed to execute ${taskType}`);
      console.error('Manual execution error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestWebScraping = async (): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/test/web_scraping`, { method: 'POST' });
      if (response.ok) {
        const result: { success: boolean; error?: string } = await response.json();
        if (result.success) {
          setError(null);
        } else {
          setError(`Web scraping test failed: ${result.error || 'Unknown error'}`);
        }
      } else {
        setError('Failed to test web scraping');
      }
    } catch (err) {
      setError('Failed to test web scraping');
      console.error('Test web scraping error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (level: string): string => {
    switch (level) {
      case 'success': return 'text-green-600';
      case 'error': return 'text-red-600';
      case 'warning': return 'text-yellow-600';
      default: return 'text-blue-600';
    }
  };

  const getStatusIcon = (level: string): React.ReactElement => {
    switch (level) {
      case 'success': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      case 'warning': return <AlertCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Wifi className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-800">WiFi Automation System</h1>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${systemStatus?.is_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm font-medium text-gray-600">
                {systemStatus?.is_running ? 'Running' : 'Stopped'}
              </span>
            </div>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6" role="alert">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                {error}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">System Status</h3>
              <p className="text-sm text-blue-600">
                {systemStatus?.is_running ? 'Active' : 'Inactive'}
              </p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-800 mb-2">Scheduler</h3>
              <p className="text-sm text-green-600">
                {systemStatus?.scheduler_status?.scheduled_jobs || 0} jobs scheduled
              </p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="font-semibold text-yellow-800 mb-2">Next Run</h3>
              <p className="text-sm text-yellow-600">
                {systemStatus?.scheduler_status?.next_run || 'None scheduled'}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-800 mb-2">WiFi URL</h3>
              <p className="text-sm text-purple-600 truncate">
                {systemStatus?.configuration?.wifi_url || 'Not configured'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-3 mb-6">
            <button
              onClick={handleStartSystem}
              disabled={loading || systemStatus?.is_running}
              className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              type="button"
            >
              <Play className="w-4 h-4" />
              <span>Start System</span>
            </button>
            <button
              onClick={handleStopSystem}
              disabled={loading || !systemStatus?.is_running}
              className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              type="button"
            >
              <Square className="w-4 h-4" />
              <span>Stop System</span>
            </button>
            <button
              onClick={handleTestWebScraping}
              disabled={loading}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              type="button"
            >
              <Download className="w-4 h-4" />
              <span>Test Web Scraping</span>
            </button>
            <button
              onClick={() => handleManualExecution('web_scraping', 1)}
              disabled={loading}
              className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              type="button"
            >
              <FileText className="w-4 h-4" />
              <span>Manual Slot 1</span>
            </button>
            <button
              onClick={() => handleManualExecution('web_scraping', 2)}
              disabled={loading}
              className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              type="button"
            >
              <FileText className="w-4 h-4" />
              <span>Manual Slot 2</span>
            </button>
            <button
              onClick={() => handleManualExecution('web_scraping', 3)}
              disabled={loading}
              className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              type="button"
            >
              <FileText className="w-4 h-4" />
              <span>Manual Slot 3</span>
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">System Logs</h2>
          <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500 text-center">No logs available</p>
            ) : (
              <div className="space-y-2">
                {logs.slice(-50).reverse().map((log, index) => (
                  <div key={`${log.timestamp}-${index}`} className="flex items-start space-x-3 text-sm">
                    <span className="text-gray-500 font-mono text-xs min-w-[140px]">
                      {log.timestamp}
                    </span>
                    <span className={`${getStatusColor(log.level)} min-w-[80px] font-medium`}>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(log.level)}
                        <span>{log.level.toUpperCase()}</span>
                      </div>
                    </span>
                    <span className="text-gray-600 min-w-[100px] font-medium">
                      {log.component}
                    </span>
                    <span className="text-gray-800 flex-1">
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;