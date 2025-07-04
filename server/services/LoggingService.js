import winston from 'winston';
import path from 'path';
import fs from 'fs-extra';

export class LoggingService {
  constructor() {
    this.logDir = path.join(process.cwd(), 'logs');
    this.initializeLogger();
  }

  async initializeLogger() {
    // Ensure logs directory exists
    await fs.ensureDir(this.logDir);

    // Create logger with multiple transports
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      ),
      defaultMeta: { service: 'wifi-automation' },
      transports: [
        // Error log file
        new winston.transports.File({
          filename: path.join(this.logDir, 'error.log'),
          level: 'error',
          maxsize: 5242880, // 5MB
          maxFiles: 5
        }),
        // Combined log file
        new winston.transports.File({
          filename: path.join(this.logDir, 'combined.log'),
          maxsize: 5242880, // 5MB
          maxFiles: 10
        }),
        // Console output
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        })
      ]
    });

    // Add database transport if available
    this.dbService = null;
  }

  setDatabaseService(dbService) {
    this.dbService = dbService;
  }

  async log(level, component, message, details = null, executionId = null) {
    const logEntry = {
      level,
      component,
      message,
      details,
      executionId,
      timestamp: new Date().toISOString()
    };

    // Log to winston
    this.logger.log(level, message, { component, details, executionId });

    // Log to database if available
    if (this.dbService) {
      try {
        await this.dbService.addLog(level, component, message, details, executionId);
      } catch (error) {
        this.logger.error('Failed to log to database:', error);
      }
    }

    return logEntry;
  }

  async info(component, message, details = null, executionId = null) {
    return await this.log('info', component, message, details, executionId);
  }

  async warn(component, message, details = null, executionId = null) {
    return await this.log('warning', component, message, details, executionId);
  }

  async error(component, message, details = null, executionId = null) {
    return await this.log('error', component, message, details, executionId);
  }

  async success(component, message, details = null, executionId = null) {
    return await this.log('success', component, message, details, executionId);
  }

  async getLogs(options = {}) {
    const { limit = 100, level = null, component = null } = options;
    
    if (this.dbService) {
      return await this.dbService.getLogs(limit, level, component);
    }
    
    return [];
  }

  async clearLogs() {
    if (this.dbService) {
      await this.dbService.run('DELETE FROM execution_logs');
    }
  }

  async exportLogs(startDate, endDate) {
    if (this.dbService) {
      return await this.dbService.all(`
        SELECT * FROM execution_logs 
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
      `, [startDate, endDate]);
    }
    
    return [];
  }
}