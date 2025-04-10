from NetworkTracker import NetworkTracker
import sys
import time
import json
import psutil
import ctypes
import os
from PyQt5.QtWidgets import QApplication, QMessageBox



class BandwidthHogKiller:
    def __init__(self):
        self.app = QApplication([])  # required for yes no dialog
        self.network_tracker = NetworkTracker()
        self.config = {}
        self.get_config()
        
    def get_config(self):
        with open('.config.json', 'r') as f:
            self.config = json.load(f)
    
    def kill_task(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            print(f"Killed process {process.name()} (PID: {pid})")
        except Exception as e:
            print(f"Failed to kill process {pid}: {e}")
            
    def update_config(self):
        with open('.config.json', 'w') as f:
            json.dump(self.config, f)
            
    def monitor_network(self):
        try:
            self.network_tracker.start_tracking()
            while True:
                try:
                    traffic_data = self.network_tracker.get_current_traffic()
                    for pid, data in traffic_data.items():
                        process = psutil.Process(pid)
                        process_name = process.name()
                        
                        print(process_name, data)
                        
                        if process_name in self.config['kill']:
                            self.kill_task(pid)
                        elif process_name in self.config['ignore']:
                            continue
                        elif data['recv'] > 0.1:
                            if (self.yes_no_dialog(process_name)):
                                self.config['kill'].append(process_name)
                                self.kill_task(pid)
                            else:
                                self.config['ignore'].append(process_name)
                            
                            self.update_config()
                except Exception as e: 
                    print(e)
                finally: 
                    time.sleep(1)
        except Exception as e:
            print(e)
    
    def yes_no_dialog(self, process_name: str) -> bool:
        dialog = f'{process_name} is using bandwidth. Do you want to kill it?'
        reply = QMessageBox.question(None, 'Confirmation', dialog,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes




def monitor_network_traffic(interval=1):
    tracker = NetworkTracker()
    try:
        tracker.start_tracking()
        while True:
            traffic_data = tracker.get_current_traffic()
            print(traffic_data)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        tracker.stop_tracking()
    
    
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    
def get_admin():
    if not is_admin():
        run_as_admin()
        sys.exit()

if __name__ == '__main__':
    get_admin()

    killer = BandwidthHogKiller()
    killer.monitor_network()  