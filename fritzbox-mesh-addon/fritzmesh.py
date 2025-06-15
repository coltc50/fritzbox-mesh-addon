import json
import os
import xml.etree.ElementTree as ET
import urllib.request
from flask import Flask, jsonify
from fritzconnection import FritzConnection
import threading
import schedule
import time

# Addon options path
options_path = '/data/options.json'
with open(options_path, 'r') as f:
    options = json.load(f)

FRITZ_IP = options.get("fritz_ip", "192.168.176.1")
USERNAME = options.get("username", "")
PASSWORD = options.get("password", "")
POLL_INTERVAL = options.get("poll_interval", 60)

mesh_data = []

def update_mesh():
    global mesh_data
    try:
        fc = FritzConnection(address=FRITZ_IP, user=USERNAME, password=PASSWORD)
        host_list_path = fc.call_action('Hosts', 'GetHostListPath')['NewHostListPath']
        with urllib.request.urlopen(f"http://{USERNAME}:{PASSWORD}@{FRITZ_IP}{host_list_path}") as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        devices = []
        for host in root.findall(".//Host"):
            name = host.find('HostName').text or ""
            ip = host.find('IPAddress').text or ""
            mac = host.find('MACAddress').text or ""
            active = host.find('Active').text or "0"
            interface = host.find('InterfaceType').text or ""
            devices.append({
                'name': name,
                'ip': ip,
                'mac': mac,
                'active': active,
                'interface': interface
            })
        mesh_data = devices
        print("Mesh updated successfully.")
    except Exception as e:
        print("Error updating mesh:", str(e))

app = Flask(__name__)

@app.route('/mesh')
def mesh():
    return jsonify(mesh_data)

def scheduler():
    schedule.every(POLL_INTERVAL).seconds.do(update_mesh)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    update_mesh()
    t = threading.Thread(target=scheduler)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=5000)
