from datetime import datetime
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

TSM_FMT = "%Y-%m-%dT%H:%M:%S"

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
            results['elapsed_time'] = (datetime.strptime(results['current_time'], TSM_FMT) - datetime.strptime(results['start_time'], TSM_FMT)).total_seconds()
            return results
    except Exception as e:
        print(f"[{ip} {cmd}] Error reading power: {e}")
        return None
    
def tasmota_start(ip):
    send_tasmota_query(ip, 'EnergyRes%205') # five decimals for energy report
    results = send_tasmota_query(ip, 'Status%208')
    send_tasmota_query(ip, 'EnergyTotal%200') # reset counter
    return results

def tasmota_stop(ip):
    send_tasmota_query(ip, 'EnergyRes%205') # five decimals for energy report
    return send_tasmota_query(ip, 'Status%208')

class A1T_Server(BaseHTTPRequestHandler):

    def do_GET(self):

        ip, cmd = self.path[1:].split('_')
        print(ip, cmd)

        if cmd == "start":
            response = tasmota_start(ip)

        elif cmd == "stop":
            response = tasmota_stop(ip)

        else:
            self.send_response(404)
            self.end_headers()
            return
        
        print(response)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, *args):  # silence logging
        return


if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 8000
    print(f"Serving on {HOST}:{PORT}")
    HTTPServer((HOST, PORT), A1T_Server).serve_forever()