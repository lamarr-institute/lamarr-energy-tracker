import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import requests
import socket

GT_FMT = "%Y-%m-%dT%H:%M:%S"
REMOTE_CONFIG_FILE = os.path.join(Path.home(), '.let', 'GT_REMOTE_CONFIG')

def send_tasmota_query(ip, cmd):
    url = f"http://{ip}/cm?cmnd={cmd}"
    try:
        r = requests.get(url, timeout=5)
        if cmd == 'Status%208':
            data = r.json()
            results = {
                'energy_total': data["StatusSNS"]["ENERGY"]["Total"] * 3600, # Wh to Ws
                'start_time': data["StatusSNS"]["ENERGY"]["TotalStartTime"],
                'current_time': data["StatusSNS"]["Time"]
            }
            results['elapsed_time'] = (datetime.strptime(results['current_time'], GT_FMT) - datetime.strptime(results['start_time'], GT_FMT)).total_seconds()
            return results
    except Exception as e:
        print(f"[{ip} {cmd}] Error reading power: {e}")
        return None
    
def tasmota_start(ip):
    send_tasmota_query(ip, 'EnergyRes%205') # five decimals for energy report
    results = send_tasmota_query(ip, 'Status%208')
    # reset all counts
    send_tasmota_query(ip, 'EnergyYesterday%200')
    send_tasmota_query(ip, 'EnergyToday%200')
    send_tasmota_query(ip, 'EnergyTotal%200')
    # update start time
    results2 = send_tasmota_query(ip, 'Status%208')
    results['current_time'] = results2['current_time']
    return results

def tasmota_stop(ip):
    send_tasmota_query(ip, 'EnergyRes%205') # five decimals for energy report
    return send_tasmota_query(ip, 'Status%208')

class GroundTruthTrackingServer:

    def __init__(self, config_file, host='0.0.0.0', port=8000):
        with open(config_file, 'r') as cf:
            self.config = json.load(cf)
        self.host = host
        self.port = port
        self.server = HTTPServer((self.host, self.port), GroundTruthTrackingRequestHandler)
        self.server.config = self.config
        print(f"Serving on {self.host}:{self.port}")
        self.server.serve_forever()

class GroundTruthTrackingRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # Example calls:
        # /list
        # /ws28/start
        # /dgx1/stop

        path = self.path[1:]

        if path == "list":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps('   '.join(list(self.server.config.keys()))).encode()
            )
            return

        try:
            hostname, cmd = path.split('/')
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return

        if hostname not in self.server.config:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Unknown hostname")
            return

        ip = self.server.config[hostname]

        if cmd == "start":
            response = tasmota_start(ip)

        elif cmd == "stop":
            response = tasmota_stop(ip)

        else:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, *args):
        return
    

class GroundTruthTracker:

    @classmethod
    def all_available(cls, server_host, server_port=8000):
        try:
            response = requests.get(f"http://{server_host}:{server_port}/list", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[GroundTruthTracker] Could not connect to server: {e}")
            return False

    @classmethod
    def is_available(cls, server_host, server_port=8000):
        available_hosts = GroundTruthTracker.all_available(server_host, server_port)
        return socket.gethostname() in available_hosts

    @classmethod
    def send_command(cls, server_host, cmd, server_port=8000):
        assert GroundTruthTracker.is_available(server_host, server_port), f"[GroundTruthTracker] The host {socket.gethostname()} is not available for tracking, please check A1T server configuration!"
        assert cmd in ['start', 'stop']
        url = f"http://{server_host}:{server_port}/{socket.gethostname()}/{cmd}"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            results = response.json()
            results['start_time'] = datetime.strptime(results['start_time'], GT_FMT)
            results['current_time'] = datetime.strptime(results['current_time'], GT_FMT)
            return results
        except Exception as e:
            raise RuntimeError(f"Command '{cmd}' failed: {e}")

    def __init__(self):

        try:
            self.server_host, self.server_port = os.environ['LET_GT_HOST'], os.environ['LET_GT_PORT']
        except KeyError:
            try:
                with open(REMOTE_CONFIG_FILE, 'r') as cf:
                    self.server_host, self.server_port = cf.read().split(':')
            except Exception:
                raise RuntimeError(f"[GroundTruthTracker] Could not initialize tracking because the remote server host and port information could not be found. Please either set the LET_GT_HOST and LET_GT_PORT environment variables, or call `python -m lamarr_energy_tracker.ground_truth_tracking --host [SERVER-IP] --port [PORT]`")
                
        # Check availability of local hostname
        self.hostname = socket.gethostname()
        try:
            if GroundTruthTracker.is_available(self.server_host, self.server_port):
                print(f"[GroundTruthTracker] Tracking for {self.hostname} with A1T Smart Sockets initialized!")
            else:
                raise RuntimeError(f"[GroundTruthTracker] Could not initialize tracking for {self.hostname} because this host is unknown to the A1T server - please check configuration!")
        except Exception:
            raise RuntimeError(f"[GroundTruthTracker] Could not connect to server at {self.server_host}:{self.server_port}, please make sure that it was correctly started!")

    def start(self):
        """Start tracking for this host"""
        results = GroundTruthTracker.send_command(self.server_host, "start", self.server_port)
        print(f"[GroundTruthTracker] Restarted tracking on {datetime.strftime(results['current_time'], GT_FMT)}, after {results['elapsed_time']/3600:7.2f} hours and {results['energy_total']/3.6e6:7.2f} kWh of tracking!")
        return results

    def stop(self):
        """Stop tracking for this host"""
        results = GroundTruthTracker.send_command(self.server_host, "stop", self.server_port)
        print(f"[GroundTruthTracker] Tracking after {results['elapsed_time']/60:7.2f} minutes standing at {results['energy_total']:12.5f} Wattseconds!")
        return results


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Either starts the server locally using the provided config, or stores the remote server HOST IP and PORT in ~/.let/ for then tracking ground-truth consumption.")
    parser.add_argument("--config", default=None, help="JSON configuration file, mapping hostnames to trackable A1T Smart Socket IPs")
    parser.add_argument("--host", default='0.0.0.0', help="Host for reaching the REST API")
    parser.add_argument("--port", default=8000, type=int, help="Port for reaching the REST API")
    args = parser.parse_args()

    if args.config:
        server = GroundTruthTrackingServer(args.config, args.host, args.port)

    else:
        os.makedirs(os.path.dirname(REMOTE_CONFIG_FILE), exist_ok=True)
        with open(REMOTE_CONFIG_FILE, 'w') as cf:
            cf.write(f'{args.host}:{args.port}')
        print(f'Stored remote tracking HOST {args.host} and PORT {args.port} in {REMOTE_CONFIG_FILE}')