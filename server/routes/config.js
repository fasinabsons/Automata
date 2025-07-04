import express from 'express';

const router = express.Router();

// Get all configuration
router.get('/', async (req, res) => {
  try {
    const { db } = req.services;
    const { category } = req.query;
    
    const config = await db.getConfig(category);
    res.json(config);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get specific configuration value
router.get('/:category/:key', async (req, res) => {
  try {
    const { db } = req.services;
    const { category, key } = req.params;
    
    const config = await db.getConfig(category, key);
    res.json(config);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Set configuration value
router.put('/:category/:key', async (req, res) => {
  try {
    const { db, logging } = req.services;
    const { category, key } = req.params;
    const { value } = req.body;
    
    await db.setConfig(category, key, value);
    
    await logging.info('Configuration', `Updated ${category}.${key}`, { value });
    
    res.json({ success: true, message: 'Configuration updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Bulk update configuration
router.put('/', async (req, res) => {
  try {
    const { db, logging } = req.services;
    const { configs } = req.body;
    
    for (const config of configs) {
      await db.setConfig(config.category, config.key, config.value);
    }
    
    await logging.info('Configuration', 'Bulk configuration update', { count: configs.length });
    
    res.json({ success: true, message: 'Configuration updated successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;