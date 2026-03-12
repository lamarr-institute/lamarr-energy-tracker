import argparse
import threading
import time
import csv
from datetime import datetime
import requests
import statistics

class SocketTracker:
    def __init__(self, ip: str, interval: int = 10, agg_window: str = 'minute', output_file: str = "power_log_{ip}.csv"):
        """
        Initialize the tracker.
        :param ip: IP address of the Tasmota socket
        :param interval: polling interval in seconds
        :param agg_window: aggregation window (writing a summary line for every {minute | hour | day})
        :param output_file: path to CSV file for windowed summaries
        """
        self.ip = ip
        self.interval = interval
        self.agg_window = agg_window
        self.output_file = output_file.format(ip=ip.replace('.', '-'))

        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

        # internal storage for measurements within current aggregation window
        self.measurements = []
        self.current_window = getattr(datetime.now(), self.agg_window)

        # start background thread immediately
        self._thread.start()
        print(f"Started tracking socket {self.ip} every {self.interval}s.")

    def _get_power(self) -> float:
        """Query the Tasmota device and return current power draw in watts."""
        url = f"http://{self.ip}/cm?cmnd=Status%208"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            return float(data["StatusSNS"]["ENERGY"]["Power"])
        except Exception as e:
            print(f"[{self.ip}] Error reading power: {e}")
            return None

    def _write_summary(self):
        """Compute min/median/max/mean/count and append to CSV."""
        
        if not self.measurements:
            print(f"[{self.ip}] No data collected this {self.current_window}.")
            return
        
        values = [v for v in self.measurements if v is not None]
        
        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": self.ip,
            "min": min(values),
            "median": statistics.median(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "count": len(values)
        }

        # write header once if file doesn’t exist yet 
        try:
            with open(self.output_file, 'x', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=summary.keys())
                writer.writeheader()
        except FileExistsError:
            pass

        with open(self.output_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=summary.keys())
            writer.writerow(summary)

        print(f"[{self.ip}] Wrote {self.agg_window}ly summary → {self.output_file}")

    def _run(self):
       """Thread loop — periodically poll the socket and handle hourly summaries."""
       while not self._stop_event.is_set():
           now_window = getattr(datetime.now(), self.agg_window)

           # Check if we’ve crossed into a new hour → write summary & reset buffer.
           if now_window != self.current_window:
               self._write_summary()
               self.measurements.clear()
               self.current_window = now_window

           value = self._get_power()
           if value is not None:
               print(f"[{self.ip}] Power={value:.2f}W")
               self.measurements.append(value)

           time.sleep(self.interval)

    def stop(self):
       """Gracefully stop tracking."""
       print(f"Stopping tracker for {self.ip}...")
       self._stop_event.set()
       self._thread.join(timeout=5)
