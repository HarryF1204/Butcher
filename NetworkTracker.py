import pydivert
import psutil
import time
from collections import defaultdict
import threading


class NetworkTracker:
    def __init__(self):
        self.bandwidth = defaultdict(lambda: {'sent': 0, 'recv': 0})
        self.conn_pid_map = {}
        self._tracking = False
        self._threads = []
    
    def update_pid_map(self):
        while self._tracking:
            self.conn_pid_map.clear()
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and conn.pid:
                    self.conn_pid_map[(conn.laddr.ip, conn.laddr.port)] = conn.pid
                if conn.raddr and conn.pid:
                    self.conn_pid_map[(conn.raddr.ip, conn.raddr.port)] = conn.pid
            time.sleep(5)

    def format_bytes(self, b):
        return f"{b / 1024:.2f} KB"

    def monitor_traffic(self):
        with pydivert.WinDivert("inbound and ip") as w:
            while self._tracking:
                try:
                    packet = w.recv()

                    ip = packet.dst_addr, packet.dst_port
                    pid = self.conn_pid_map.get(ip)
                    if pid:
                        self.bandwidth[pid]['recv'] += len(packet.raw)

                    # Forward the packet no matter what
                    try:
                        w.send(packet)
                    except OSError:
                        continue
                except Exception as e:
                    print("Packet error:", e)
                finally:
                    time.sleep(0.1)
    
    def start_tracking(self):
        self._tracking = True
        self._threads = [
            threading.Thread(target=self.update_pid_map, daemon=True),
            threading.Thread(target=self.monitor_traffic, daemon=True)
        ]
        for thread in self._threads:
            thread.start()
    
    def stop_tracking(self):
        self._tracking = False
        for thread in self._threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        self._threads = []
        
    def get_current_traffic(self):
        return dict(self.bandwidth)
        
    def track_traffic_generator(self, interval=1.0):
        if not self._tracking:
            self.start_tracking()
            
        try:
            while self._tracking:
                yield self.get_current_traffic()
                time.sleep(interval)
        finally:
            # This ensures tracking stops if the generator is closed
            if self._tracking:
                self.stop_tracking()
