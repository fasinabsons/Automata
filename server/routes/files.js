import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs-extra';

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = path.join(process.cwd(), 'uploads');
    await fs.ensureDir(uploadDir);
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    cb(null, `${timestamp}-${file.originalname}`);
  }
});

const upload = multer({ storage });

// Get file records
router.get('/records', async (req, res) => {
  try {
    const { db } = req.services;
    const { date, status } = req.query;
    
    const records = await db.getFileRecords(date, status);
    res.json(records);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Upload file
router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const { db, logging } = req.services;
    const { slot_number, execution_date } = req.body;
    
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    const fileRecord = await db.addFileRecord(
      req.file.filename,
      req.file.path,
      req.file.mimetype,
      req.file.size,
      parseInt(slot_number),
      execution_date
    );
    
    await logging.info('FileManager', `File uploaded: ${req.file.filename}`);
    
    res.json({
      success: true,
      file: {
        id: fileRecord,
        filename: req.file.filename,
        size: req.file.size,
        type: req.file.mimetype
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Download file
router.get('/download/:id', async (req, res) => {
  try {
    const { db } = req.services;
    const { id } = req.params;
    
    const fileRecord = await db.get('SELECT * FROM file_records WHERE id = ?', [id]);
    
    if (!fileRecord) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    if (!await fs.pathExists(fileRecord.file_path)) {
      return res.status(404).json({ error: 'File not found on disk' });
    }
    
    res.download(fileRecord.file_path, fileRecord.filename);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete file
router.delete('/:id', async (req, res) => {
  try {
    const { db, logging } = req.services;
    const { id } = req.params;
    
    const fileRecord = await db.get('SELECT * FROM file_records WHERE id = ?', [id]);
    
    if (!fileRecord) {
      return res.status(404).json({ error: 'File not found' });
    }
    
    // Delete from filesystem
    if (await fs.pathExists(fileRecord.file_path)) {
      await fs.remove(fileRecord.file_path);
    }
    
    // Delete from database
    await db.run('DELETE FROM file_records WHERE id = ?', [id]);
    
    await logging.info('FileManager', `File deleted: ${fileRecord.filename}`);
    
    res.json({ success: true, message: 'File deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get file statistics
router.get('/stats', async (req, res) => {
  try {
    const { db } = req.services;
    
    const stats = await db.get(`
      SELECT 
        COUNT(*) as total_files,
        SUM(size) as total_size,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_files,
        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_files,
        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_files
      FROM file_records
    `);
    
    res.json(stats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;