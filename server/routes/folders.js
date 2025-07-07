const express = require('express');
const fs = require('fs-extra');
const path = require('path');
const router = express.Router();

// Configuration file path
const CONFIG_FILE = path.join(__dirname, '../../config/folder_config.json');

// Default configuration
const DEFAULT_CONFIG = {
  csvBaseDir: 'EHC_Data',
  mergeBaseDir: 'EHC_Data_Merge',
  pdfBaseDir: 'EHC_Data_Pdf',
  autoCreateFolders: true,
  dateFormat: 'DDmonth'
};

// Helper function to get date folder name
function getDateFolderName(date = new Date(), format = 'DDmonth') {
  const day = date.getDate().toString().padStart(2, '0');
  const month = date.toLocaleDateString('en-GB', { month: 'long' }).toLowerCase();
  const year = date.getFullYear();
  const monthNum = (date.getMonth() + 1).toString().padStart(2, '0');
  
  switch (format) {
    case 'DDmonth':
      return `${day}${month}`;
    case 'DDMMYYYY':
      return `${day}${monthNum}${year}`;
    case 'YYYY-MM-DD':
      return `${year}-${monthNum}-${day}`;
    default:
      return `${day}${month}`;
  }
}

// Helper function to get folder statistics
async function getFolderStats(config) {
  const stats = {
    totalFolders: 0,
    totalFiles: 0,
    totalSizeMB: 0,
    lastUpdated: new Date().toISOString()
  };

  try {
    const baseDirs = [config.csvBaseDir, config.mergeBaseDir, config.pdfBaseDir];
    
    for (const baseDir of baseDirs) {
      if (await fs.pathExists(baseDir)) {
        const items = await fs.readdir(baseDir);
        
        for (const item of items) {
          const itemPath = path.join(baseDir, item);
          const stat = await fs.stat(itemPath);
          
          if (stat.isDirectory()) {
            stats.totalFolders++;
            
            // Count files in subdirectory
            try {
              const files = await fs.readdir(itemPath);
              for (const file of files) {
                const filePath = path.join(itemPath, file);
                const fileStat = await fs.stat(filePath);
                
                if (fileStat.isFile()) {
                  stats.totalFiles++;
                  stats.totalSizeMB += fileStat.size / (1024 * 1024);
                }
              }
            } catch (error) {
              // Skip if can't read directory
            }
          }
        }
      }
    }
    
    stats.totalSizeMB = Math.round(stats.totalSizeMB * 100) / 100;
  } catch (error) {
    console.error('Error calculating folder stats:', error);
  }

  return stats;
}

// Load configuration
async function loadConfig() {
  try {
    if (await fs.pathExists(CONFIG_FILE)) {
      const config = await fs.readJson(CONFIG_FILE);
      return { ...DEFAULT_CONFIG, ...config };
    }
  } catch (error) {
    console.error('Error loading config:', error);
  }
  return DEFAULT_CONFIG;
}

// Save configuration
async function saveConfig(config) {
  try {
    await fs.ensureDir(path.dirname(CONFIG_FILE));
    await fs.writeJson(CONFIG_FILE, config, { spaces: 2 });
    return true;
  } catch (error) {
    console.error('Error saving config:', error);
    return false;
  }
}

// GET /api/config/folders - Get folder configuration
router.get('/config/folders', async (req, res) => {
  try {
    const config = await loadConfig();
    res.json(config);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/config/folders - Save folder configuration
router.post('/config/folders', async (req, res) => {
  try {
    const config = { ...DEFAULT_CONFIG, ...req.body };
    
    // Validate configuration
    if (!config.csvBaseDir || !config.mergeBaseDir || !config.pdfBaseDir) {
      return res.status(400).json({ error: 'All base directories are required' });
    }
    
    const success = await saveConfig(config);
    
    if (success) {
      res.json({ message: 'Configuration saved successfully', config });
    } else {
      res.status(500).json({ error: 'Failed to save configuration' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/stats/folders - Get folder statistics
router.get('/stats/folders', async (req, res) => {
  try {
    const config = await loadConfig();
    const stats = await getFolderStats(config);
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/folders/create-today - Create today's folders
router.post('/folders/create-today', async (req, res) => {
  try {
    const config = await loadConfig();
    const dateFolder = getDateFolderName(new Date(), config.dateFormat);
    
    const createdFolders = [];
    const baseDirs = [
      { name: 'CSV', path: config.csvBaseDir },
      { name: 'Excel', path: config.mergeBaseDir },
      { name: 'PDF', path: config.pdfBaseDir }
    ];
    
    for (const baseDir of baseDirs) {
      const folderPath = path.join(baseDir.path, dateFolder);
      
      if (!(await fs.pathExists(folderPath))) {
        await fs.ensureDir(folderPath);
        createdFolders.push(`${baseDir.name}: ${folderPath}`);
      }
    }
    
    res.json({
      message: 'Folders created successfully',
      dateFolder,
      createdFolders,
      totalCreated: createdFolders.length
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/folders/create-date - Create folders for specific date
router.post('/folders/create-date', async (req, res) => {
  try {
    const { date } = req.body;
    
    if (!date) {
      return res.status(400).json({ error: 'Date is required' });
    }
    
    const config = await loadConfig();
    const targetDate = new Date(date);
    const dateFolder = getDateFolderName(targetDate, config.dateFormat);
    
    const createdFolders = [];
    const baseDirs = [
      { name: 'CSV', path: config.csvBaseDir },
      { name: 'Excel', path: config.mergeBaseDir },
      { name: 'PDF', path: config.pdfBaseDir }
    ];
    
    for (const baseDir of baseDirs) {
      const folderPath = path.join(baseDir.path, dateFolder);
      
      if (!(await fs.pathExists(folderPath))) {
        await fs.ensureDir(folderPath);
        createdFolders.push(`${baseDir.name}: ${folderPath}`);
      }
    }
    
    res.json({
      message: 'Folders created successfully',
      dateFolder,
      createdFolders,
      totalCreated: createdFolders.length
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/folders/list - List all date folders
router.get('/folders/list', async (req, res) => {
  try {
    const config = await loadConfig();
    const folders = {};
    
    const baseDirs = [
      { name: 'csv', path: config.csvBaseDir },
      { name: 'merge', path: config.mergeBaseDir },
      { name: 'pdf', path: config.pdfBaseDir }
    ];
    
    for (const baseDir of baseDirs) {
      folders[baseDir.name] = [];
      
      if (await fs.pathExists(baseDir.path)) {
        const items = await fs.readdir(baseDir.path);
        
        for (const item of items) {
          const itemPath = path.join(baseDir.path, item);
          const stat = await fs.stat(itemPath);
          
          if (stat.isDirectory()) {
            // Get folder stats
            const files = await fs.readdir(itemPath);
            const fileCount = files.length;
            let totalSize = 0;
            
            for (const file of files) {
              try {
                const filePath = path.join(itemPath, file);
                const fileStat = await fs.stat(filePath);
                if (fileStat.isFile()) {
                  totalSize += fileStat.size;
                }
              } catch (error) {
                // Skip if can't read file
              }
            }
            
            folders[baseDir.name].push({
              name: item,
              path: itemPath,
              fileCount,
              totalSizeMB: Math.round(totalSize / (1024 * 1024) * 100) / 100,
              lastModified: stat.mtime.toISOString()
            });
          }
        }
        
        // Sort by name (date)
        folders[baseDir.name].sort((a, b) => a.name.localeCompare(b.name));
      }
    }
    
    res.json(folders);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// DELETE /api/folders/cleanup - Clean up old folders
router.delete('/folders/cleanup', async (req, res) => {
  try {
    const { daysToKeep = 30 } = req.body;
    const config = await loadConfig();
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
    
    const cleanupResults = {
      csv: 0,
      merge: 0,
      pdf: 0,
      errors: []
    };
    
    const baseDirs = [
      { name: 'csv', path: config.csvBaseDir },
      { name: 'merge', path: config.mergeBaseDir },
      { name: 'pdf', path: config.pdfBaseDir }
    ];
    
    for (const baseDir of baseDirs) {
      if (await fs.pathExists(baseDir.path)) {
        const items = await fs.readdir(baseDir.path);
        
        for (const item of items) {
          const itemPath = path.join(baseDir.path, item);
          const stat = await fs.stat(itemPath);
          
          if (stat.isDirectory()) {
            try {
              // Parse date from folder name (basic implementation)
              const folderDate = new Date(stat.birthtime);
              
              if (folderDate < cutoffDate) {
                await fs.remove(itemPath);
                cleanupResults[baseDir.name]++;
              }
            } catch (error) {
              cleanupResults.errors.push(`Failed to clean ${itemPath}: ${error.message}`);
            }
          }
        }
      }
    }
    
    res.json({
      message: 'Cleanup completed',
      results: cleanupResults,
      totalCleaned: cleanupResults.csv + cleanupResults.merge + cleanupResults.pdf
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 