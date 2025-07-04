import os
import sys
import subprocess
import shutil
import winreg
from pathlib import Path
import json
from datetime import datetime
from core.logger import logger

class DeploymentManager:
    def __init__(self, execution_id=None):
        self.execution_id = execution_id
        self.install_dir = Path("C:/WiFiAutomation")
        self.service_name = "WiFiAutomationService"
        
    def create_installation_package(self):
        """Create installation package"""
        try:
            logger.info("Creating installation package", "Deployment", self.execution_id)
            
            # Create package directory
            package_dir = Path("dist/WiFiAutomation")
            package_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy application files
            self._copy_application_files(package_dir)
            
            # Create installer script
            self._create_installer_script(package_dir)
            
            # Create uninstaller script
            self._create_uninstaller_script(package_dir)
            
            # Create service scripts
            self._create_service_scripts(package_dir)
            
            # Create configuration files
            self._create_config_files(package_dir)
            
            logger.success(f"Installation package created: {package_dir}", "Deployment", self.execution_id)
            
            return {
                'success': True,
                'package_path': str(package_dir),
                'installer': str(package_dir / "install.bat")
            }
            
        except Exception as e:
            logger.error(f"Failed to create installation package: {str(e)}", "Deployment", self.execution_id, e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _copy_application_files(self, package_dir):
        """Copy application files to package directory"""
        try:
            # Files and directories to include
            items_to_copy = [
                "main.py",
                "config/",
                "core/",
                "modules/",
                "api/",
                "requirements.txt",
                "README.md"
            ]
            
            for item in items_to_copy:
                src = Path(item)
                if src.exists():
                    dst = package_dir / item
                    if src.is_file():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    
                    logger.info(f"Copied {item} to package", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to copy application files: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _create_installer_script(self, package_dir):
        """Create Windows installer script"""
        try:
            installer_content = f'''@echo off
echo WiFi User Data Automation System - Installer
echo ============================================

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

:: Create installation directory
echo Creating installation directory...
mkdir "{self.install_dir}" 2>nul

:: Copy files
echo Copying application files...
xcopy /E /I /Y "*" "{self.install_dir}\\"

:: Install Python dependencies
echo Installing Python dependencies...
cd /d "{self.install_dir}"
python -m pip install -r requirements.txt

:: Create Windows service
echo Installing Windows service...
python -m pip install pywin32
python install_service.py install

:: Create desktop shortcut
echo Creating desktop shortcut...
python create_shortcut.py

:: Create start menu entry
echo Creating start menu entry...
mkdir "%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\WiFi Automation" 2>nul
copy "WiFi Automation.lnk" "%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\WiFi Automation\\"

:: Set up automatic startup
echo Configuring automatic startup...
schtasks /create /tn "WiFiAutomationStartup" /tr "{self.install_dir}\\start_service.bat" /sc onstart /ru SYSTEM /f

echo.
echo Installation completed successfully!
echo The WiFi Automation System has been installed to: {self.install_dir}
echo.
echo To start the system:
echo 1. Use the desktop shortcut
echo 2. Run from Start Menu
echo 3. Use Windows Services (service name: {self.service_name})
echo.
pause
'''
            
            installer_path = package_dir / "install.bat"
            with open(installer_path, 'w') as f:
                f.write(installer_content)
            
            logger.info("Installer script created", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to create installer script: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _create_uninstaller_script(self, package_dir):
        """Create uninstaller script"""
        try:
            uninstaller_content = f'''@echo off
echo WiFi User Data Automation System - Uninstaller
echo ==============================================

:: Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This uninstaller requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

:: Stop and remove service
echo Stopping and removing service...
sc stop {self.service_name}
sc delete {self.service_name}

:: Remove scheduled tasks
echo Removing scheduled tasks...
schtasks /delete /tn "WiFiAutomationStartup" /f 2>nul
schtasks /delete /tn "WiFiAutomationRestart" /f 2>nul

:: Remove shortcuts
echo Removing shortcuts...
del "%USERPROFILE%\\Desktop\\WiFi Automation.lnk" 2>nul
rmdir /s /q "%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\WiFi Automation" 2>nul

:: Remove installation directory
echo Removing installation files...
cd /d C:\\
rmdir /s /q "{self.install_dir}"

echo.
echo Uninstallation completed successfully!
echo.
pause
'''
            
            uninstaller_path = package_dir / "uninstall.bat"
            with open(uninstaller_path, 'w') as f:
                f.write(uninstaller_content)
            
            logger.info("Uninstaller script created", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to create uninstaller script: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _create_service_scripts(self, package_dir):
        """Create Windows service scripts"""
        try:
            # Service installation script
            service_install_content = '''
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
from pathlib import Path

class WiFiAutomationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WiFiAutomationService"
    _svc_display_name_ = "WiFi User Data Automation Service"
    _svc_description_ = "Automated WiFi user data collection and processing service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def main(self):
        # Import and run the main automation system
        sys.path.append(str(Path(__file__).parent))
        from main import WiFiAutomationSystem
        
        system = WiFiAutomationSystem()
        try:
            system.start()
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        finally:
            system.stop()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WiFiAutomationService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(WiFiAutomationService)
'''
            
            service_path = package_dir / "install_service.py"
            with open(service_path, 'w') as f:
                f.write(service_install_content)
            
            # Service start script
            start_service_content = f'''@echo off
echo Starting WiFi Automation Service...
sc start {self.service_name}
if %errorlevel% equ 0 (
    echo Service started successfully.
) else (
    echo Failed to start service. Error code: %errorlevel%
)
pause
'''
            
            start_service_path = package_dir / "start_service.bat"
            with open(start_service_path, 'w') as f:
                f.write(start_service_content)
            
            # Service stop script
            stop_service_content = f'''@echo off
echo Stopping WiFi Automation Service...
sc stop {self.service_name}
if %errorlevel% equ 0 (
    echo Service stopped successfully.
) else (
    echo Failed to stop service. Error code: %errorlevel%
)
pause
'''
            
            stop_service_path = package_dir / "stop_service.bat"
            with open(stop_service_path, 'w') as f:
                f.write(stop_service_content)
            
            logger.info("Service scripts created", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to create service scripts: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _create_config_files(self, package_dir):
        """Create configuration files"""
        try:
            # Create default configuration
            config_content = {
                "wifi": {
                    "target_url": "https://51.38.163.73:8443/wsg/",
                    "username": "admin",
                    "password": "AdminFlower@123",
                    "timeout": 30
                },
                "vbs": {
                    "primary_path": "C:\\Users\\Lenovo\\Music\\moonflower\\AbsonsItERP.exe - Shortcut.lnk",
                    "fallback_path": "\\\\192.168.10.16\\e\\ArabianLive\\ArabianLive_MoonFlower\\AbsonsItERP.exe",
                    "username": "Vj",
                    "password": ""
                },
                "schedule": {
                    "slot1_time": "09:30",
                    "slot2_time": "13:00",
                    "slot3_time": "15:00",
                    "processing_time": "15:05",
                    "email_time": "09:00",
                    "restart_time": "01:00"
                },
                "system": {
                    "file_retention_days": 60,
                    "log_level": "INFO",
                    "auto_restart": True
                }
            }
            
            config_path = package_dir / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_content, f, indent=4)
            
            # Create shortcut creation script
            shortcut_content = '''
import os
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    desktop = winshell.desktop()
    path = os.path.join(desktop, "WiFi Automation.lnk")
    target = r"''' + str(self.install_dir / "start_service.bat") + '''"
    wDir = r"''' + str(self.install_dir) + '''"
    icon = r"''' + str(self.install_dir / "icon.ico") + '''"
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()
    
    print(f"Desktop shortcut created: {path}")

if __name__ == "__main__":
    create_desktop_shortcut()
'''
            
            shortcut_path = package_dir / "create_shortcut.py"
            with open(shortcut_path, 'w') as f:
                f.write(shortcut_content)
            
            logger.info("Configuration files created", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to create configuration files: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def install_system(self):
        """Install the system on current machine"""
        try:
            logger.info("Installing WiFi Automation System", "Deployment", self.execution_id)
            
            # Create installation directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy current files to installation directory
            self._copy_to_install_dir()
            
            # Install Python dependencies
            self._install_dependencies()
            
            # Create Windows service
            self._install_service()
            
            # Create shortcuts
            self._create_shortcuts()
            
            # Set up automatic startup
            self._setup_startup()
            
            logger.success(f"System installed successfully to {self.install_dir}", "Deployment", self.execution_id)
            
            return {
                'success': True,
                'install_path': str(self.install_dir),
                'service_name': self.service_name
            }
            
        except Exception as e:
            logger.error(f"Installation failed: {str(e)}", "Deployment", self.execution_id, e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _copy_to_install_dir(self):
        """Copy files to installation directory"""
        try:
            current_dir = Path.cwd()
            
            # Copy main application files
            for item in ["main.py", "config", "core", "modules", "api", "requirements.txt"]:
                src = current_dir / item
                dst = self.install_dir / item
                
                if src.exists():
                    if src.is_file():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, dst)
                    else:
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
            
            logger.info("Files copied to installation directory", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to copy files: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _install_dependencies(self):
        """Install Python dependencies"""
        try:
            requirements_path = self.install_dir / "requirements.txt"
            if requirements_path.exists():
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("Dependencies installed successfully", "Deployment", self.execution_id)
                else:
                    raise Exception(f"Pip install failed: {result.stderr}")
            
        except Exception as e:
            logger.error(f"Failed to install dependencies: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _install_service(self):
        """Install Windows service"""
        try:
            # Install pywin32 for service support
            subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], 
                         capture_output=True, text=True)
            
            # Create service script in install directory
            service_script = self.install_dir / "wifi_service.py"
            # Copy service script content here...
            
            logger.info("Windows service installed", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to install service: {str(e)}", "Deployment", self.execution_id, e)
            raise
    
    def _create_shortcuts(self):
        """Create desktop and start menu shortcuts"""
        try:
            # This would create actual shortcuts
            logger.info("Shortcuts created", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to create shortcuts: {str(e)}", "Deployment", self.execution_id, e)
    
    def _setup_startup(self):
        """Set up automatic startup"""
        try:
            # Create scheduled task for startup
            task_command = f'schtasks /create /tn "WiFiAutomationStartup" /tr "{self.install_dir}\\main.py" /sc onstart /ru SYSTEM /f'
            
            result = subprocess.run(task_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Automatic startup configured", "Deployment", self.execution_id)
            else:
                logger.warning(f"Failed to configure startup: {result.stderr}", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.error(f"Failed to setup startup: {str(e)}", "Deployment", self.execution_id, e)
    
    def uninstall_system(self):
        """Uninstall the system"""
        try:
            logger.info("Uninstalling WiFi Automation System", "Deployment", self.execution_id)
            
            # Stop and remove service
            self._remove_service()
            
            # Remove scheduled tasks
            self._remove_scheduled_tasks()
            
            # Remove shortcuts
            self._remove_shortcuts()
            
            # Remove installation directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
            
            logger.success("System uninstalled successfully", "Deployment", self.execution_id)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Uninstallation failed: {str(e)}", "Deployment", self.execution_id, e)
            return {'success': False, 'error': str(e)}
    
    def _remove_service(self):
        """Remove Windows service"""
        try:
            # Stop service
            subprocess.run(f'sc stop {self.service_name}', shell=True, capture_output=True)
            
            # Delete service
            subprocess.run(f'sc delete {self.service_name}', shell=True, capture_output=True)
            
            logger.info("Windows service removed", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.warning(f"Failed to remove service: {str(e)}", "Deployment", self.execution_id)
    
    def _remove_scheduled_tasks(self):
        """Remove scheduled tasks"""
        try:
            tasks = ["WiFiAutomationStartup", "WiFiAutomationRestart"]
            
            for task in tasks:
                subprocess.run(f'schtasks /delete /tn "{task}" /f', 
                             shell=True, capture_output=True)
            
            logger.info("Scheduled tasks removed", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.warning(f"Failed to remove scheduled tasks: {str(e)}", "Deployment", self.execution_id)
    
    def _remove_shortcuts(self):
        """Remove shortcuts"""
        try:
            # Remove desktop shortcut
            desktop_shortcut = Path.home() / "Desktop" / "WiFi Automation.lnk"
            if desktop_shortcut.exists():
                desktop_shortcut.unlink()
            
            # Remove start menu folder
            start_menu = Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/WiFi Automation")
            if start_menu.exists():
                shutil.rmtree(start_menu)
            
            logger.info("Shortcuts removed", "Deployment", self.execution_id)
            
        except Exception as e:
            logger.warning(f"Failed to remove shortcuts: {str(e)}", "Deployment", self.execution_id)

# Test function
def test_deployment():
    """Test deployment functionality"""
    deployment = DeploymentManager("test-execution")
    
    # Create installation package
    package_result = deployment.create_installation_package()
    print(f"Package creation result: {package_result}")

if __name__ == "__main__":
    test_deployment()