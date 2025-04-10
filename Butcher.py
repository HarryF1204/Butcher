import ctypes
import subprocess
import sys
import atexit
import signal

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_admin():
    script = sys.argv[0]
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {params}', None, 1
    )

def cleanup_processes(proc1, proc2):
    print('Cleaning up processes...')
    for proc in (proc1, proc2):
        try:
            proc.terminate()
            proc.wait(timeout=3)  # Wait up to 3 seconds for graceful termination
        except:
            try:
                proc.kill()  # Force kill if terminate doesn't work
            except:
                pass
    print('Butcher has terminated.')

if __name__ == "__main__":
    if not is_admin():
        run_admin()
        sys.exit()
    
    proc1 = subprocess.Popen(["python", "./disableWindowsBandwidthHogs.py"], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
    proc2 = subprocess.Popen(["python", "./killBandwidthHogTasks.py"], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    # Register cleanup function to run on exit
    atexit.register(cleanup_processes, proc1, proc2)
    
    print('Butcher is running...')
    
    input("Press Enter to exit...")
    
    cleanup_processes(proc1, proc2)
    atexit.unregister(cleanup_processes)  # Prevent double cleanup
