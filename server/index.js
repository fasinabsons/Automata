import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Import route modules
import systemRoutes from './routes/system.js';
import schedulerRoutes from './routes/scheduler.js';
import filesRoutes from './routes/files.js';
import logsRoutes from './routes/logs.js';
import configRoutes from './routes/config.js';
import automationRoutes from './routes/automation.js';

// Import services
import { DatabaseService } from './services/DatabaseService.js';
import { LoggingService } from './services/LoggingService.js';
import { SchedulerService } from './services/SchedulerService.js';
import { WebSocketService } from './services/WebSocketService.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Initialize services
const dbService = new DatabaseService();
const loggingService = new LoggingService();
const schedulerService = new SchedulerService(dbService, loggingService);
const wsService = new WebSocketService(wss, loggingService);

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../dist')));

// Make services available to routes
app.use((req, res, next) => {
  req.services = {
    db: dbService,
    logging: loggingService,
    scheduler: schedulerService,
    websocket: wsService
  };
  next();
});

// Routes
app.use('/api/system', systemRoutes);
app.use('/api/scheduler', schedulerRoutes);
app.use('/api/files', filesRoutes);
app.use('/api/logs', logsRoutes);
app.use('/api/config', configRoutes);
app.use('/api/automation', automationRoutes);

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../dist/index.html'));
});

// Initialize database and start server
async function startServer() {
  try {
    await dbService.initialize();
    await schedulerService.initialize();
    
    const PORT = process.env.PORT || 3001;
    server.listen(PORT, () => {
      loggingService.info(`Server running on port ${PORT}`);
      console.log(`🚀 WiFi Automation System running on http://localhost:${PORT}`);
    });
  } catch (error) {
    loggingService.error('Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  loggingService.info('Received SIGTERM, shutting down gracefully');
  await schedulerService.stop();
  await dbService.close();
  process.exit(0);
});

startServer();