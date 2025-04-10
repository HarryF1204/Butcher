import ctypes
import subprocess
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_admin():
    # Relaunch the script with admin privileges
    script = sys.argv[0]
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {params}', None, 1
    )

def stop_and_disable_service(service_name):
    print(f"Stopping and disabling {service_name}...")
    subprocess.run(["sc", "stop", service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sc", "config", service_name, "start=", "disabled"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    if not is_admin():
        print("Restarting with admin privileges...")
        run_admin()
        sys.exit()

    services = ["wuauserv", "DoSvc", "BITS"]
    for svc in services:
        stop_and_disable_service(svc)

    print("All targeted services have been stopped and disabled.")
    input("Press Enter to exit...")
