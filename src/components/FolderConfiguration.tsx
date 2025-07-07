import React, { useState, useEffect } from 'react';
import { FolderOpen, Settings, Save, RefreshCw } from 'lucide-react';

interface FolderConfig {
  csvBaseDir: string;
  mergeBaseDir: string;
  pdfBaseDir: string;
  autoCreateFolders: boolean;
  dateFormat: string;
}

interface FolderStats {
  totalFolders: number;
  totalFiles: number;
  totalSizeMB: number;
  lastUpdated: string;
}

const FolderConfiguration: React.FC = () => {
  const [config, setConfig] = useState<FolderConfig>({
    csvBaseDir: 'EHC_Data',
    mergeBaseDir: 'EHC_Data_Merge',
    pdfBaseDir: 'EHC_Data_Pdf',
    autoCreateFolders: true,
    dateFormat: 'DDmonth'
  });
  
  const [stats, setStats] = useState<FolderStats>({
    totalFolders: 0,
    totalFiles: 0,
    totalSizeMB: 0,
    lastUpdated: ''
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');

  // Load configuration on component mount
  useEffect(() => {
    loadConfiguration();
    loadStats();
  }, []);

  const loadConfiguration = async () => {
    try {
      const response = await fetch('/api/config/folders');
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (error) {
      console.error('Failed to load configuration:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/stats/folders');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const saveConfiguration = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/config/folders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        setMessage('Configuration saved successfully!');
        setMessageType('success');
        await loadStats(); // Refresh stats
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      setMessage('Failed to save configuration');
      setMessageType('error');
    } finally {
      setIsLoading(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const createTodayFolders = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/folders/create-today', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(`Created folders for ${data.dateFolder}`);
        setMessageType('success');
        await loadStats();
      } else {
        throw new Error('Failed to create folders');
      }
    } catch (error) {
      setMessage('Failed to create today\'s folders');
      setMessageType('error');
    } finally {
      setIsLoading(false);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleInputChange = (field: keyof FolderConfig, value: string | boolean) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const selectFolder = async (field: keyof FolderConfig) => {
    try {
      // This would open a folder dialog in a real implementation
      // For now, we'll just show an info message
      setMessage('Folder selection dialog would open here');
      setMessageType('info');
      setTimeout(() => setMessage(''), 2000);
    } catch (error) {
      console.error('Folder selection failed:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Settings className="h-6 w-6 text-blue-600" />
          <h2 className="text-xl font-semibold text-gray-900">Folder Configuration</h2>
        </div>
        <button
          onClick={loadStats}
          className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`mb-4 p-3 rounded-md ${
          messageType === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
          messageType === 'error' ? 'bg-red-50 text-red-800 border border-red-200' :
          'bg-blue-50 text-blue-800 border border-blue-200'
        }`}>
          {message}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Folders</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalFolders}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Files</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalFiles}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Size</div>
          <div className="text-2xl font-bold text-gray-900">{stats.totalSizeMB.toFixed(1)} MB</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Last Updated</div>
          <div className="text-sm font-medium text-gray-900">{stats.lastUpdated}</div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="space-y-6">
        {/* CSV Base Directory */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CSV Base Directory
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={config.csvBaseDir}
              onChange={(e) => handleInputChange('csvBaseDir', e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="EHC_Data"
            />
            <button
              onClick={() => selectFolder('csvBaseDir')}
              className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              <FolderOpen className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Base directory for CSV files (date folders will be created inside)
          </p>
        </div>

        {/* Excel Merge Directory */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Excel Merge Directory
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={config.mergeBaseDir}
              onChange={(e) => handleInputChange('mergeBaseDir', e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="EHC_Data_Merge"
            />
            <button
              onClick={() => selectFolder('mergeBaseDir')}
              className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              <FolderOpen className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Base directory for Excel files (date folders will be created inside)
          </p>
        </div>

        {/* PDF Reports Directory */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            PDF Reports Directory
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={config.pdfBaseDir}
              onChange={(e) => handleInputChange('pdfBaseDir', e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="EHC_Data_Pdf"
            />
            <button
              onClick={() => selectFolder('pdfBaseDir')}
              className="px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              <FolderOpen className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            Base directory for PDF files (date folders will be created inside)
          </p>
        </div>

        {/* Date Format */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date Folder Format
          </label>
          <select
            value={config.dateFormat}
            onChange={(e) => handleInputChange('dateFormat', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="DDmonth">DDmonth (e.g., 05july)</option>
            <option value="DDMMYYYY">DDMMYYYY (e.g., 05072025)</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD (e.g., 2025-07-05)</option>
          </select>
          <p className="text-sm text-gray-500 mt-1">
            Format for date-based folder names
          </p>
        </div>

        {/* Auto Create Folders */}
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="autoCreateFolders"
            checked={config.autoCreateFolders}
            onChange={(e) => handleInputChange('autoCreateFolders', e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="autoCreateFolders" className="text-sm font-medium text-gray-700">
            Automatically create date folders when needed
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
        <button
          onClick={createTodayFolders}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <FolderOpen className="h-4 w-4" />
          <span>Create Today's Folders</span>
        </button>

        <button
          onClick={saveConfiguration}
          disabled={isLoading}
          className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Save className="h-4 w-4" />
          <span>{isLoading ? 'Saving...' : 'Save Configuration'}</span>
        </button>
      </div>

      {/* Folder Structure Preview */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Folder Structure Preview</h3>
        <div className="text-sm text-gray-600 space-y-1">
          <div>📁 {config.csvBaseDir}/</div>
          <div className="ml-4">📁 {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long' }).replace(' ', '').toLowerCase()}/</div>
          <div className="ml-8">📄 clients.csv, clients(1).csv, ...</div>
          <div>📁 {config.mergeBaseDir}/</div>
          <div className="ml-4">📁 {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long' }).replace(' ', '').toLowerCase()}/</div>
          <div className="ml-8">📄 EHC_Upload_Mac_{new Date().toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '')}.xls</div>
          <div>📁 {config.pdfBaseDir}/</div>
          <div className="ml-4">📁 {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long' }).replace(' ', '').toLowerCase()}/</div>
          <div className="ml-8">📄 moon flower active users_{new Date().toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '')}.pdf</div>
        </div>
      </div>
    </div>
  );
};

export default FolderConfiguration; 