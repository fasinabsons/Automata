export class WebSocketService {
  constructor(wss, loggingService) {
    this.wss = wss;
    this.loggingService = loggingService;
    this.clients = new Set();
    this.initialize();
  }

  initialize() {
    this.wss.on('connection', (ws) => {
      this.clients.add(ws);
      
      ws.on('close', () => {
        this.clients.delete(ws);
      });

      ws.on('error', (error) => {
        this.loggingService.error('WebSocket', 'WebSocket error', error.message);
        this.clients.delete(ws);
      });

      // Send initial connection message
      this.sendToClient(ws, {
        type: 'connection',
        message: 'Connected to WiFi Automation System',
        timestamp: new Date().toISOString()
      });
    });
  }

  sendToClient(ws, data) {
    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }

  broadcast(data) {
    const message = JSON.stringify(data);
    this.clients.forEach(client => {
      if (client.readyState === client.OPEN) {
        client.send(message);
      }
    });
  }

  broadcastSystemStatus(status) {
    this.broadcast({
      type: 'system_status',
      data: status,
      timestamp: new Date().toISOString()
    });
  }

  broadcastLog(logEntry) {
    this.broadcast({
      type: 'log',
      data: logEntry,
      timestamp: new Date().toISOString()
    });
  }

  broadcastExecutionUpdate(executionData) {
    this.broadcast({
      type: 'execution_update',
      data: executionData,
      timestamp: new Date().toISOString()
    });
  }

  broadcastFileUpdate(fileData) {
    this.broadcast({
      type: 'file_update',
      data: fileData,
      timestamp: new Date().toISOString()
    });
  }

  getClientCount() {
    return this.clients.size;
  }
}