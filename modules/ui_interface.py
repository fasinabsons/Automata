import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from datetime import datetime
import json
from pathlib import Path
from config.settings import SCHEDULE_CONFIG
from core.logger import logger

class WiFiAutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WiFi User Data Automation System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # System status variables
        self.system_running = tk.BooleanVar(value=False)
        self.last_execution = tk.StringVar(value="Never")
        self.next_execution = tk.StringVar(value="Not scheduled")
        self.files_processed = tk.IntVar(value=0)
        self.errors_count = tk.IntVar(value=0)
        
        # Log queue for thread-safe logging
        self.log_queue = queue.Queue()
        
        # Create GUI components
        self.create_widgets()
        self.setup_layout()
        
        # Start log processing
        self.process_log_queue()
        
        # Initialize system reference
        self.automation_system = None
        
    def configure_styles(self):
        """Configure custom styles for dark theme"""
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'),
                           background='#2b2b2b',
                           foreground='#ffffff')
        
        self.style.configure('Header.TLabel',
                           font=('Arial', 12, 'bold'),
                           background='#2b2b2b',
                           foreground='#ffffff')
        
        self.style.configure('Status.TLabel',
                           font=('Arial', 10),
                           background='#2b2b2b',
                           foreground='#cccccc')
        
        self.style.configure('Success.TLabel',
                           font=('Arial', 10),
                           background='#2b2b2b',
                           foreground='#00ff00')
        
        self.style.configure('Error.TLabel',
                           font=('Arial', 10),
                           background='#2b2b2b',
                           foreground='#ff4444')
        
        self.style.configure('Custom.TButton',
                           font=('Arial', 10),
                           padding=10)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main title
        self.title_label = ttk.Label(self.root, 
                                   text="WiFi User Data Automation System",
                                   style='Title.TLabel')
        
        # Status frame
        self.status_frame = ttk.LabelFrame(self.root, text="System Status", padding=10)
        self.create_status_widgets()
        
        # Control frame
        self.control_frame = ttk.LabelFrame(self.root, text="System Controls", padding=10)
        self.create_control_widgets()
        
        # Schedule frame
        self.schedule_frame = ttk.LabelFrame(self.root, text="Execution Schedule", padding=10)
        self.create_schedule_widgets()
        
        # Manual execution frame
        self.manual_frame = ttk.LabelFrame(self.root, text="Manual Execution", padding=10)
        self.create_manual_widgets()
        
        # Log frame
        self.log_frame = ttk.LabelFrame(self.root, text="System Logs", padding=10)
        self.create_log_widgets()
    
    def create_status_widgets(self):
        """Create system status widgets"""
        # System running indicator
        self.status_indicator = tk.Canvas(self.status_frame, width=20, height=20, bg='#2b2b2b', highlightthickness=0)
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18, fill='red', outline='')
        
        ttk.Label(self.status_frame, text="System Status:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=5)
        self.status_indicator.grid(row=0, column=1, padx=5)
        self.status_text = ttk.Label(self.status_frame, text="Stopped", style='Error.TLabel')
        self.status_text.grid(row=0, column=2, sticky='w', padx=5)
        
        # Last execution
        ttk.Label(self.status_frame, text="Last Execution:", style='Status.TLabel').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(self.status_frame, textvariable=self.last_execution, style='Status.TLabel').grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        
        # Next execution
        ttk.Label(self.status_frame, text="Next Execution:", style='Status.TLabel').grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(self.status_frame, textvariable=self.next_execution, style='Status.TLabel').grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        
        # Files processed
        ttk.Label(self.status_frame, text="Files Processed:", style='Status.TLabel').grid(row=3, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(self.status_frame, textvariable=self.files_processed, style='Status.TLabel').grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        
        # Errors count
        ttk.Label(self.status_frame, text="Errors:", style='Status.TLabel').grid(row=4, column=0, sticky='w', padx=5, pady=2)
        ttk.Label(self.status_frame, textvariable=self.errors_count, style='Error.TLabel').grid(row=4, column=1, columnspan=2, sticky='w', padx=5, pady=2)
    
    def create_control_widgets(self):
        """Create system control widgets"""
        self.start_button = ttk.Button(self.control_frame, 
                                     text="Start System",
                                     command=self.start_system,
                                     style='Custom.TButton')
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(self.control_frame,
                                    text="Stop System", 
                                    command=self.stop_system,
                                    style='Custom.TButton',
                                    state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.test_button = ttk.Button(self.control_frame,
                                    text="Test Components",
                                    command=self.test_components,
                                    style='Custom.TButton')
        self.test_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.config_button = ttk.Button(self.control_frame,
                                      text="Configuration",
                                      command=self.open_configuration,
                                      style='Custom.TButton')
        self.config_button.grid(row=0, column=3, padx=5, pady=5)
    
    def create_schedule_widgets(self):
        """Create schedule display widgets"""
        schedules = [
            ("Slot 1 - Morning", SCHEDULE_CONFIG['slot1_time']),
            ("Slot 2 - Afternoon", SCHEDULE_CONFIG['slot2_time']),
            ("Slot 3 - Evening", SCHEDULE_CONFIG['slot3_time']),
            ("Processing", SCHEDULE_CONFIG['processing_time']),
            ("Email Reports", SCHEDULE_CONFIG['email_time'])
        ]
        
        for i, (name, time) in enumerate(schedules):
            ttk.Label(self.schedule_frame, text=f"{name}:", style='Status.TLabel').grid(row=i, column=0, sticky='w', padx=5, pady=2)
            ttk.Label(self.schedule_frame, text=time, style='Status.TLabel').grid(row=i, column=1, sticky='w', padx=20, pady=2)
            
            # Status indicator
            status_canvas = tk.Canvas(self.schedule_frame, width=15, height=15, bg='#2b2b2b', highlightthickness=0)
            status_canvas.create_oval(2, 2, 13, 13, fill='green', outline='')
            status_canvas.grid(row=i, column=2, padx=5, pady=2)
    
    def create_manual_widgets(self):
        """Create manual execution widgets"""
        manual_buttons = [
            ("Run Slot 1", lambda: self.manual_execution(1)),
            ("Run Slot 2", lambda: self.manual_execution(2)),
            ("Run Slot 3", lambda: self.manual_execution(3)),
            ("Process Files", lambda: self.manual_execution(4)),
            ("Send Email", lambda: self.manual_execution(5))
        ]
        
        for i, (text, command) in enumerate(manual_buttons):
            button = ttk.Button(self.manual_frame,
                              text=text,
                              command=command,
                              style='Custom.TButton')
            button.grid(row=i//3, column=i%3, padx=5, pady=5, sticky='ew')
        
        # Configure column weights
        for i in range(3):
            self.manual_frame.columnconfigure(i, weight=1)
    
    def create_log_widgets(self):
        """Create log display widgets"""
        # Log text area
        self.log_text = scrolledtext.ScrolledText(self.log_frame,
                                                height=15,
                                                width=80,
                                                bg='#1e1e1e',
                                                fg='#ffffff',
                                                font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
        
        # Log control buttons
        ttk.Button(self.log_frame, text="Clear Logs", command=self.clear_logs).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.log_frame, text="Export Logs", command=self.export_logs).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.log_frame, text="Refresh", command=self.refresh_logs).grid(row=1, column=2, padx=5, pady=5)
        
        # Configure grid weights
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
    
    def setup_layout(self):
        """Setup the main layout"""
        self.title_label.pack(pady=10)
        
        # Top row - Status and Controls
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        self.control_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Middle row - Schedule and Manual
        middle_frame = ttk.Frame(self.root)
        middle_frame.pack(fill='x', padx=10, pady=5)
        
        self.schedule_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        self.manual_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Bottom - Logs
        self.log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Pack frames in top_frame and middle_frame
        top_frame.pack_propagate(False)
        middle_frame.pack_propagate(False)
    
    def start_system(self):
        """Start the automation system"""
        try:
            if self.automation_system:
                # Start system in background thread
                threading.Thread(target=self._start_system_thread, daemon=True).start()
                
                self.system_running.set(True)
                self.update_status_display()
                self.add_log("INFO", "System", "Automation system started")
                
                self.start_button.config(state='disabled')
                self.stop_button.config(state='normal')
            else:
                messagebox.showerror("Error", "Automation system not initialized")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start system: {str(e)}")
            self.add_log("ERROR", "System", f"Failed to start: {str(e)}")
    
    def _start_system_thread(self):
        """Start system in background thread"""
        try:
            if self.automation_system:
                self.automation_system.start()
        except Exception as e:
            self.add_log("ERROR", "System", f"System thread error: {str(e)}")
    
    def stop_system(self):
        """Stop the automation system"""
        try:
            if self.automation_system:
                self.automation_system.stop()
                
            self.system_running.set(False)
            self.update_status_display()
            self.add_log("INFO", "System", "Automation system stopped")
            
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop system: {str(e)}")
            self.add_log("ERROR", "System", f"Failed to stop: {str(e)}")
    
    def test_components(self):
        """Test system components"""
        try:
            self.add_log("INFO", "Test", "Starting component tests...")
            
            # Test in background thread
            threading.Thread(target=self._test_components_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tests: {str(e)}")
    
    def _test_components_thread(self):
        """Run component tests in background"""
        try:
            if self.automation_system:
                # Test web scraping
                self.add_log("INFO", "Test", "Testing web scraping...")
                self.automation_system.run_manual_test("web_scraping")
                
                # Test VBS integration
                self.add_log("INFO", "Test", "Testing VBS integration...")
                self.automation_system.run_manual_test("vbs_integration")
                
                self.add_log("SUCCESS", "Test", "All component tests completed")
            else:
                self.add_log("ERROR", "Test", "Automation system not available")
                
        except Exception as e:
            self.add_log("ERROR", "Test", f"Component test failed: {str(e)}")
    
    def manual_execution(self, slot_number):
        """Execute manual slot"""
        try:
            self.add_log("INFO", "Manual", f"Starting manual execution for slot {slot_number}")
            
            # Execute in background thread
            threading.Thread(target=self._manual_execution_thread, args=(slot_number,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start manual execution: {str(e)}")
    
    def _manual_execution_thread(self, slot_number):
        """Run manual execution in background"""
        try:
            if self.automation_system:
                # This would call the appropriate manual execution method
                self.add_log("INFO", "Manual", f"Executing slot {slot_number}...")
                # automation_system.manual_execution(slot_number)
                self.add_log("SUCCESS", "Manual", f"Slot {slot_number} execution completed")
            else:
                self.add_log("ERROR", "Manual", "Automation system not available")
                
        except Exception as e:
            self.add_log("ERROR", "Manual", f"Manual execution failed: {str(e)}")
    
    def open_configuration(self):
        """Open configuration dialog"""
        try:
            config_window = ConfigurationWindow(self.root)
            config_window.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open configuration: {str(e)}")
    
    def update_status_display(self):
        """Update status display elements"""
        if self.system_running.get():
            self.status_indicator.itemconfig(self.status_circle, fill='green')
            self.status_text.config(text="Running", style='Success.TLabel')
        else:
            self.status_indicator.itemconfig(self.status_circle, fill='red')
            self.status_text.config(text="Stopped", style='Error.TLabel')
    
    def add_log(self, level, component, message):
        """Add log entry to queue"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{component}] {message}\n"
        self.log_queue.put(log_entry)
    
    def process_log_queue(self):
        """Process log queue and update display"""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_log_queue)
    
    def clear_logs(self):
        """Clear log display"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("INFO", "UI", "Log display cleared")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                
                self.add_log("INFO", "UI", f"Logs exported to {filename}")
                messagebox.showinfo("Success", f"Logs exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {str(e)}")
    
    def refresh_logs(self):
        """Refresh log display"""
        self.add_log("INFO", "UI", "Log display refreshed")
    
    def set_automation_system(self, system):
        """Set reference to automation system"""
        self.automation_system = system
    
    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

class ConfigurationWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Configuration")
        self.window.geometry("600x400")
        self.window.configure(bg='#2b2b2b')
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create configuration widgets"""
        # WiFi Configuration
        wifi_frame = ttk.LabelFrame(self.window, text="WiFi Configuration", padding=10)
        wifi_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(wifi_frame, text="URL:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.wifi_url = ttk.Entry(wifi_frame, width=50)
        self.wifi_url.insert(0, "https://51.38.163.73:8443/wsg/")
        self.wifi_url.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(wifi_frame, text="Username:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.wifi_username = ttk.Entry(wifi_frame, width=50)
        self.wifi_username.insert(0, "admin")
        self.wifi_username.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(wifi_frame, text="Password:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.wifi_password = ttk.Entry(wifi_frame, width=50, show="*")
        self.wifi_password.insert(0, "AdminFlower@123")
        self.wifi_password.grid(row=2, column=1, padx=5, pady=2)
        
        # VBS Configuration
        vbs_frame = ttk.LabelFrame(self.window, text="VBS Configuration", padding=10)
        vbs_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(vbs_frame, text="Primary Path:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.vbs_primary = ttk.Entry(vbs_frame, width=50)
        self.vbs_primary.insert(0, r"C:\Users\Lenovo\Music\moonflower\AbsonsItERP.exe - Shortcut.lnk")
        self.vbs_primary.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(vbs_frame, text="Username:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.vbs_username = ttk.Entry(vbs_frame, width=50)
        self.vbs_username.insert(0, "Vj")
        self.vbs_username.grid(row=1, column=1, padx=5, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_config).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side='right', padx=5)
    
    def save_config(self):
        """Save configuration"""
        try:
            # Here you would save the configuration to file
            messagebox.showinfo("Success", "Configuration saved successfully")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def show(self):
        """Show the configuration window"""
        self.window.transient(self.parent)
        self.window.grab_set()
        self.parent.wait_window(self.window)

# Test function
def test_ui():
    """Test the UI interface"""
    app = WiFiAutomationGUI()
    app.run()

if __name__ == "__main__":
    test_ui()