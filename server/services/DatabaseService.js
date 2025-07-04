import sqlite3 from 'sqlite3';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs-extra';

export class DatabaseService {
  constructor() {
    this.db = null;
    this.dbPath = path.join(process.cwd(), 'data', 'automation.db');
  }

  async initialize() {
    try {
      // Ensure data directory exists
      await fs.ensureDir(path.dirname(this.dbPath));
      
      this.db = new sqlite3.Database(this.dbPath);
      
      // Promisify database methods
      this.run = promisify(this.db.run.bind(this.db));
      this.get = promisify(this.db.get.bind(this.db));
      this.all = promisify(this.db.all.bind(this.db));
      
      await this.createTables();
      console.log('Database initialized successfully');
    } catch (error) {
      console.error('Database initialization failed:', error);
      throw error;
    }
  }

  async createTables() {
    const tables = [
      // System status table
      `CREATE TABLE IF NOT EXISTS system_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        is_running BOOLEAN DEFAULT 0,
        last_execution DATETIME,
        next_execution DATETIME,
        current_slot INTEGER,
        files_processed INTEGER DEFAULT 0,
        errors INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // Execution logs table
      `CREATE TABLE IF NOT EXISTS execution_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        level TEXT NOT NULL,
        component TEXT NOT NULL,
        message TEXT NOT NULL,
        details TEXT,
        execution_id TEXT
      )`,

      // Schedule configuration table
      `CREATE TABLE IF NOT EXISTS schedule_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_number INTEGER UNIQUE,
        time TEXT NOT NULL,
        enabled BOOLEAN DEFAULT 1,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )`,

      // File processing records
      `CREATE TABLE IF NOT EXISTS file_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        size INTEGER,
        status TEXT DEFAULT 'pending',
        slot_number INTEGER,
        execution_date DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        processed_at DATETIME
      )`,

      // Configuration settings
      `CREATE TABLE IF NOT EXISTS config_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(category, key)
      )`,

      // Execution history
      `CREATE TABLE IF NOT EXISTS execution_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id TEXT UNIQUE NOT NULL,
        slot_number INTEGER,
        start_time DATETIME,
        end_time DATETIME,
        status TEXT DEFAULT 'running',
        files_downloaded INTEGER DEFAULT 0,
        files_processed INTEGER DEFAULT 0,
        errors INTEGER DEFAULT 0,
        details TEXT
      )`
    ];

    for (const table of tables) {
      await this.run(table);
    }

    // Insert default data
    await this.insertDefaultData();
  }

  async insertDefaultData() {
    // Default system status
    const existingStatus = await this.get('SELECT id FROM system_status LIMIT 1');
    if (!existingStatus) {
      await this.run(`
        INSERT INTO system_status (is_running, files_processed, errors)
        VALUES (0, 0, 0)
      `);
    }

    // Default schedule configuration
    const schedules = [
      { slot_number: 1, time: '09:30', description: 'Morning Collection' },
      { slot_number: 2, time: '13:00', description: 'Afternoon Collection' },
      { slot_number: 3, time: '15:00', description: 'Evening Collection' },
      { slot_number: 4, time: '15:05', description: 'File Processing & VBS Upload' },
      { slot_number: 5, time: '21:00', description: 'Email Report Generation' }
    ];

    for (const schedule of schedules) {
      await this.run(`
        INSERT OR IGNORE INTO schedule_config (slot_number, time, description)
        VALUES (?, ?, ?)
      `, [schedule.slot_number, schedule.time, schedule.description]);
    }

    // Default configuration settings
    const configs = [
      { category: 'wifi', key: 'target_url', value: 'https://51.38.163.73:8443/wsg/', description: 'WiFi management interface URL' },
      { category: 'wifi', key: 'username', value: 'admin', description: 'WiFi interface username' },
      { category: 'wifi', key: 'password', value: 'AdminFlower@123', description: 'WiFi interface password' },
      { category: 'vbs', key: 'primary_path', value: 'C:\\Users\\Lenovo\\Music\\moonflower\\AbsonsItERP.exe - Shortcut.lnk', description: 'Primary VBS application path' },
      { category: 'vbs', key: 'fallback_path', value: '\\\\192.168.10.16\\e\\ArabianLive\\ArabianLive_MoonFlower\\AbsonsItERP.exe', description: 'Fallback VBS application path' },
      { category: 'vbs', key: 'username', value: 'Vj', description: 'VBS application username' },
      { category: 'vbs', key: 'password', value: '', description: 'VBS application password' },
      { category: 'email', key: 'enabled', value: 'true', description: 'Enable email reports' },
      { category: 'email', key: 'send_time', value: '09:00', description: 'Daily email send time' },
      { category: 'system', key: 'restart_time', value: '01:00', description: 'Daily system restart time' },
      { category: 'system', key: 'file_retention_days', value: '60', description: 'File retention period in days' }
    ];

    for (const config of configs) {
      await this.run(`
        INSERT OR IGNORE INTO config_settings (category, key, value, description)
        VALUES (?, ?, ?, ?)
      `, [config.category, config.key, config.value, config.description]);
    }
  }

  // System status methods
  async getSystemStatus() {
    return await this.get('SELECT * FROM system_status ORDER BY id DESC LIMIT 1');
  }

  async updateSystemStatus(updates) {
    const fields = Object.keys(updates).map(key => `${key} = ?`).join(', ');
    const values = Object.values(updates);
    values.push(new Date().toISOString());
    
    await this.run(`
      UPDATE system_status 
      SET ${fields}, updated_at = ?
      WHERE id = (SELECT id FROM system_status ORDER BY id DESC LIMIT 1)
    `, values);
  }

  // Logging methods
  async addLog(level, component, message, details = null, executionId = null) {
    await this.run(`
      INSERT INTO execution_logs (level, component, message, details, execution_id)
      VALUES (?, ?, ?, ?, ?)
    `, [level, component, message, details, executionId]);
  }

  async getLogs(limit = 100, level = null, component = null) {
    let query = 'SELECT * FROM execution_logs';
    const params = [];
    const conditions = [];

    if (level) {
      conditions.push('level = ?');
      params.push(level);
    }

    if (component) {
      conditions.push('component = ?');
      params.push(component);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY timestamp DESC LIMIT ?';
    params.push(limit);

    return await this.all(query, params);
  }

  // Schedule methods
  async getScheduleConfig() {
    return await this.all('SELECT * FROM schedule_config ORDER BY slot_number');
  }

  async updateScheduleSlot(slotNumber, time, enabled, description) {
    await this.run(`
      UPDATE schedule_config 
      SET time = ?, enabled = ?, description = ?, updated_at = CURRENT_TIMESTAMP
      WHERE slot_number = ?
    `, [time, enabled, description, slotNumber]);
  }

  // File records methods
  async addFileRecord(filename, filePath, fileType, size, slotNumber, executionDate) {
    await this.run(`
      INSERT INTO file_records (filename, file_path, file_type, size, slot_number, execution_date)
      VALUES (?, ?, ?, ?, ?, ?)
    `, [filename, filePath, fileType, size, slotNumber, executionDate]);
  }

  async updateFileStatus(id, status, processedAt = null) {
    await this.run(`
      UPDATE file_records 
      SET status = ?, processed_at = ?
      WHERE id = ?
    `, [status, processedAt || new Date().toISOString(), id]);
  }

  async getFileRecords(date = null, status = null) {
    let query = 'SELECT * FROM file_records';
    const params = [];
    const conditions = [];

    if (date) {
      conditions.push('execution_date = ?');
      params.push(date);
    }

    if (status) {
      conditions.push('status = ?');
      params.push(status);
    }

    if (conditions.length > 0) {
      query += ' WHERE ' + conditions.join(' AND ');
    }

    query += ' ORDER BY created_at DESC';

    return await this.all(query, params);
  }

  // Configuration methods
  async getConfig(category = null, key = null) {
    if (category && key) {
      return await this.get('SELECT * FROM config_settings WHERE category = ? AND key = ?', [category, key]);
    } else if (category) {
      return await this.all('SELECT * FROM config_settings WHERE category = ?', [category]);
    } else {
      return await this.all('SELECT * FROM config_settings ORDER BY category, key');
    }
  }

  async setConfig(category, key, value) {
    await this.run(`
      INSERT OR REPLACE INTO config_settings (category, key, value, updated_at)
      VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    `, [category, key, value]);
  }

  // Execution history methods
  async startExecution(executionId, slotNumber) {
    await this.run(`
      INSERT INTO execution_history (execution_id, slot_number, start_time, status)
      VALUES (?, ?, CURRENT_TIMESTAMP, 'running')
    `, [executionId, slotNumber]);
  }

  async updateExecution(executionId, updates) {
    const fields = Object.keys(updates).map(key => `${key} = ?`).join(', ');
    const values = Object.values(updates);
    values.push(executionId);
    
    await this.run(`
      UPDATE execution_history 
      SET ${fields}
      WHERE execution_id = ?
    `, values);
  }

  async getExecutionHistory(limit = 50) {
    return await this.all(`
      SELECT * FROM execution_history 
      ORDER BY start_time DESC 
      LIMIT ?
    `, [limit]);
  }

  async close() {
    if (this.db) {
      this.db.close();
    }
  }
}