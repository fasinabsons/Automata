import express from 'express';

const router = express.Router();

// Get logs
router.get('/', async (req, res) => {
  try {
    const { logging } = req.services;
    const { limit = 100, level, component } = req.query;
    
    const logs = await logging.getLogs({
      limit: parseInt(limit),
      level,
      component
    });
    
    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Clear logs
router.delete('/', async (req, res) => {
  try {
    const { logging } = req.services;
    await logging.clearLogs();
    res.json({ success: true, message: 'Logs cleared successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Export logs
router.get('/export', async (req, res) => {
  try {
    const { logging } = req.services;
    const { start_date, end_date } = req.query;
    
    const logs = await logging.exportLogs(start_date, end_date);
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Content-Disposition', 'attachment; filename=logs.json');
    res.json(logs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Add manual log entry
router.post('/', async (req, res) => {
  try {
    const { logging } = req.services;
    const { level, component, message, details } = req.body;
    
    const logEntry = await logging.log(level, component, message, details);
    res.json(logEntry);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;