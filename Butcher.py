import ctypes
import subprocess
import sys

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

if __name__ == "__main__":
    if not is_admin():
        run_admin()
        sys.exit()
    
    proc1 = subprocess.Popen(["python", "./disableWindowsBandwidthHogs.py"], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
    proc2 = subprocess.Popen(["python", "./killBandwidthHogTasks.py"], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print('Butcher is running...')
    
    input("Press Enter to exit...")
    
    proc1.terminate()
    proc2.terminate()
    proc1.wait()
    proc2.wait()
    print('Butcher has terminated.')

