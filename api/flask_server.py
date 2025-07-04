from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import json
from datetime import datetime
from pathlib import Path

# Import automation modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from main import WiFiAutomationSystem
from modules.scheduler import automation_scheduler
from core.logger import logger

app = Flask(__name__)
CORS(app)

# Global system instance
wifi_system = WiFiAutomationSystem()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        status = wifi_system.get_system_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/start', methods=['POST'])
def start_system():
    """Start the automation system"""
    try:
        if not wifi_system.is_running:
            # Start in background thread
            thread = threading.Thread(target=wifi_system.start, daemon=True)
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'System started successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'System is already running',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_system():
    """Stop the automation system"""
    try:
        wifi_system.stop()
        return jsonify({
            'success': True,
            'message': 'System stopped successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/execute/<task_type>', methods=['POST'])
def manual_execute(task_type):
    """Execute task manually"""
    try:
        data = request.get_json() or {}
        
        if task_type == 'web_scraping':
            slot_number = data.get('slot_number', 1)
            automation_scheduler.manual_execution('web_scraping', slot_number=slot_number)
            message = f'Web scraping started for slot {slot_number}'
            
        elif task_type == 'vbs_processing':
            automation_scheduler.manual_execution('vbs_processing')
            message = 'VBS processing started'
            
        elif task_type == 'email_reports':
            automation_scheduler.manual_execution('email_reports')
            message = 'Email reports started'
            
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown task type: {task_type}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        return jsonify({
            'success': True,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get system logs"""
    try:
        # Read recent logs from file
        log_file = Path("logs/automation.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                recent_logs = lines[-100:] if len(lines) > 100 else lines
                
            return jsonify({
                'success': True,
                'data': {
                    'logs': [line.strip() for line in recent_logs],
                    'count': len(recent_logs)
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'logs': [],
                    'count': 0
                },
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/test/<component>', methods=['POST'])
def test_component(component):
    """Test specific component"""
    try:
        wifi_system.run_manual_test(component)
        
        return jsonify({
            'success': True,
            'message': f'{component} test completed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'WiFi Automation System',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Starting Flask API server", "API")
    app.run(host='0.0.0.0', port=5000, debug=False)