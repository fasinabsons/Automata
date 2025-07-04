import express from 'express';

const router = express.Router();

// Get system status
router.get('/status', async (req, res) => {
  try {
    const { db, scheduler } = req.services;
    
    const systemStatus = await db.getSystemStatus();
    const nextExecution = await scheduler.getNextExecution();
    const schedulerStatus = scheduler.getStatus();

    res.json({
      ...systemStatus,
      next_execution: nextExecution?.time?.toISOString(),
      scheduler_status: schedulerStatus
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update system status
router.put('/status', async (req, res) => {
  try {
    const { db, websocket } = req.services;
    const updates = req.body;
    
    await db.updateSystemStatus(updates);
    const updatedStatus = await db.getSystemStatus();
    
    websocket.broadcastSystemStatus(updatedStatus);
    
    res.json(updatedStatus);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start/stop system
router.post('/control/:action', async (req, res) => {
  try {
    const { action } = req.params;
    const { scheduler, logging, db, websocket } = req.services;
    
    if (action === 'start') {
      await scheduler.start();
      await db.updateSystemStatus({ is_running: true });
      await logging.info('System', 'System started manually');
    } else if (action === 'stop') {
      await scheduler.stop();
      await db.updateSystemStatus({ is_running: false });
      await logging.info('System', 'System stopped manually');
    } else {
      return res.status(400).json({ error: 'Invalid action' });
    }
    
    const updatedStatus = await db.getSystemStatus();
    websocket.broadcastSystemStatus(updatedStatus);
    
    res.json({ success: true, action, status: updatedStatus });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Manual execution
router.post('/execute/:slot', async (req, res) => {
  try {
    const { slot } = req.params;
    const { scheduler, logging } = req.services;
    
    const slotNumber = parseInt(slot);
    if (isNaN(slotNumber) || slotNumber < 1 || slotNumber > 5) {
      return res.status(400).json({ error: 'Invalid slot number' });
    }
    
    await logging.info('System', `Manual execution requested for slot ${slotNumber}`);
    
    // Execute in background
    scheduler.manualExecution(slotNumber).catch(error => {
      logging.error('System', `Manual execution failed for slot ${slotNumber}`, error.message);
    });
    
    res.json({ success: true, message: `Execution started for slot ${slotNumber}` });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get execution history
router.get('/history', async (req, res) => {
  try {
    const { db } = req.services;
    const { limit = 50 } = req.query;
    
    const history = await db.getExecutionHistory(parseInt(limit));
    res.json(history);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;