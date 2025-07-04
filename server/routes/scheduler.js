import express from 'express';

const router = express.Router();

// Get schedule configuration
router.get('/config', async (req, res) => {
  try {
    const { db } = req.services;
    const scheduleConfig = await db.getScheduleConfig();
    res.json(scheduleConfig);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update schedule configuration
router.put('/config/:slot', async (req, res) => {
  try {
    const { slot } = req.params;
    const { time, enabled, description } = req.body;
    const { scheduler, logging } = req.services;
    
    const slotNumber = parseInt(slot);
    if (isNaN(slotNumber)) {
      return res.status(400).json({ error: 'Invalid slot number' });
    }
    
    await scheduler.updateSchedule(slotNumber, time, enabled, description);
    
    res.json({ success: true, message: 'Schedule updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get next execution
router.get('/next', async (req, res) => {
  try {
    const { scheduler } = req.services;
    const nextExecution = await scheduler.getNextExecution();
    res.json(nextExecution);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get scheduler status
router.get('/status', async (req, res) => {
  try {
    const { scheduler } = req.services;
    const status = scheduler.getStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;