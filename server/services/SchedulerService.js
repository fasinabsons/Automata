import cron from 'node-cron';
import { v4 as uuidv4 } from 'uuid';

export class SchedulerService {
  constructor(dbService, loggingService) {
    this.dbService = dbService;
    this.loggingService = loggingService;
    this.scheduledTasks = new Map();
    this.isRunning = false;
  }

  async initialize() {
    try {
      await this.loadScheduleFromDatabase();
      await this.loggingService.info('Scheduler', 'Scheduler service initialized successfully');
    } catch (error) {
      await this.loggingService.error('Scheduler', 'Failed to initialize scheduler', error.message);
      throw error;
    }
  }

  async loadScheduleFromDatabase() {
    const scheduleConfig = await this.dbService.getScheduleConfig();
    
    // Clear existing tasks
    this.scheduledTasks.forEach(task => task.destroy());
    this.scheduledTasks.clear();

    // Create new scheduled tasks
    for (const config of scheduleConfig) {
      if (config.enabled) {
        await this.scheduleTask(config);
      }
    }
  }

  async scheduleTask(config) {
    const [hour, minute] = config.time.split(':');
    const cronExpression = `${minute} ${hour} * * *`;

    try {
      const task = cron.schedule(cronExpression, async () => {
        await this.executeSlot(config.slot_number, config.description);
      }, {
        scheduled: false,
        timezone: 'America/New_York' // Adjust timezone as needed
      });

      this.scheduledTasks.set(config.slot_number, task);
      task.start();

      await this.loggingService.info('Scheduler', 
        `Scheduled task for slot ${config.slot_number} at ${config.time}`, 
        { slotNumber: config.slot_number, time: config.time, description: config.description }
      );
    } catch (error) {
      await this.loggingService.error('Scheduler', 
        `Failed to schedule task for slot ${config.slot_number}`, 
        error.message
      );
    }
  }

  async executeSlot(slotNumber, description) {
    const executionId = uuidv4();
    
    try {
      await this.loggingService.info('Scheduler', 
        `Starting execution for ${description}`, 
        null, 
        executionId
      );

      // Update system status
      await this.dbService.updateSystemStatus({
        is_running: true,
        current_slot: slotNumber,
        last_execution: new Date().toISOString()
      });

      // Start execution record
      await this.dbService.startExecution(executionId, slotNumber);

      // Execute based on slot type
      let result;
      switch (slotNumber) {
        case 1:
        case 2:
        case 3:
          result = await this.executeWebScraping(slotNumber, executionId);
          break;
        case 4:
          result = await this.executeFileProcessing(executionId);
          break;
        case 5:
          result = await this.executeEmailReport(executionId);
          break;
        default:
          throw new Error(`Unknown slot number: ${slotNumber}`);
      }

      // Update execution record
      await this.dbService.updateExecution(executionId, {
        end_time: new Date().toISOString(),
        status: 'completed',
        files_downloaded: result.filesDownloaded || 0,
        files_processed: result.filesProcessed || 0,
        details: JSON.stringify(result)
      });

      await this.loggingService.success('Scheduler', 
        `Completed execution for ${description}`, 
        result, 
        executionId
      );

    } catch (error) {
      await this.loggingService.error('Scheduler', 
        `Failed execution for ${description}`, 
        error.message, 
        executionId
      );

      // Update execution record with error
      await this.dbService.updateExecution(executionId, {
        end_time: new Date().toISOString(),
        status: 'failed',
        details: JSON.stringify({ error: error.message })
      });

      // Increment error count
      const currentStatus = await this.dbService.getSystemStatus();
      await this.dbService.updateSystemStatus({
        errors: (currentStatus.errors || 0) + 1
      });
    } finally {
      // Update system status
      await this.dbService.updateSystemStatus({
        is_running: false,
        current_slot: null
      });
    }
  }

  async executeWebScraping(slotNumber, executionId) {
    await this.loggingService.info('WebScraping', 
      `Starting web scraping for slot ${slotNumber}`, 
      null, 
      executionId
    );

    // This would integrate with the actual web scraping module
    // For now, return mock data
    return {
      filesDownloaded: 4,
      sources: ['EHC TV', 'EHC-15', 'Reception Hall-Mobile', 'Reception Hall-TV'],
      executionTime: '45 seconds'
    };
  }

  async executeFileProcessing(executionId) {
    await this.loggingService.info('FileProcessing', 
      'Starting file processing and VBS upload', 
      null, 
      executionId
    );

    // This would integrate with the actual file processing module
    // For now, return mock data
    return {
      filesProcessed: 1,
      excelGenerated: true,
      vbsUploadSuccess: true,
      reportGenerated: true,
      executionTime: '2 minutes'
    };
  }

  async executeEmailReport(executionId) {
    await this.loggingService.info('EmailReport', 
      'Starting email report generation', 
      null, 
      executionId
    );

    // This would integrate with the actual email module
    // For now, return mock data
    return {
      emailSent: true,
      recipients: ['admin@moonflower.com'],
      reportDate: new Date().toISOString().split('T')[0],
      executionTime: '10 seconds'
    };
  }

  async manualExecution(slotNumber) {
    const config = await this.dbService.get(
      'SELECT * FROM schedule_config WHERE slot_number = ?', 
      [slotNumber]
    );
    
    if (!config) {
      throw new Error(`No configuration found for slot ${slotNumber}`);
    }

    await this.executeSlot(slotNumber, `Manual: ${config.description}`);
  }

  async updateSchedule(slotNumber, time, enabled, description) {
    await this.dbService.updateScheduleSlot(slotNumber, time, enabled, description);
    await this.loadScheduleFromDatabase();
    
    await this.loggingService.info('Scheduler', 
      `Updated schedule for slot ${slotNumber}`, 
      { time, enabled, description }
    );
  }

  async getNextExecution() {
    const scheduleConfig = await this.dbService.getScheduleConfig();
    const now = new Date();
    let nextExecution = null;

    for (const config of scheduleConfig) {
      if (!config.enabled) continue;

      const [hour, minute] = config.time.split(':');
      const scheduledTime = new Date();
      scheduledTime.setHours(parseInt(hour), parseInt(minute), 0, 0);

      // If the time has passed today, schedule for tomorrow
      if (scheduledTime <= now) {
        scheduledTime.setDate(scheduledTime.getDate() + 1);
      }

      if (!nextExecution || scheduledTime < nextExecution.time) {
        nextExecution = {
          time: scheduledTime,
          slot: config.slot_number,
          description: config.description
        };
      }
    }

    return nextExecution;
  }

  async start() {
    this.isRunning = true;
    this.scheduledTasks.forEach(task => task.start());
    await this.loggingService.info('Scheduler', 'Scheduler started');
  }

  async stop() {
    this.isRunning = false;
    this.scheduledTasks.forEach(task => task.stop());
    await this.loggingService.info('Scheduler', 'Scheduler stopped');
  }

  getStatus() {
    return {
      isRunning: this.isRunning,
      activeTasks: this.scheduledTasks.size,
      tasks: Array.from(this.scheduledTasks.keys())
    };
  }
}