#!/usr/bin/env python3
import threading
import queue
import json
import collections
from datetime import datetime, timezone

from common.config      import drone_args
from drone.battery      import Battery
from drone.drone_client import CentralClient
from drone.drone_server import start_server
from drone.gui          import start_gui

def processor_loop(data_q, client: CentralClient, battery: Battery, threshold: float):
    window = collections.deque(maxlen=10)

    while True:
        addr, text = data_q.get()
        reading = json.loads(text)
        temp      = reading.get("temperature")
        hum       = reading.get("humidity")
        ts        = reading.get("timestamp")

        window.append(reading)
        avg_temp = sum(r["temperature"] for r in window) / len(window)
        avg_hum  = sum(r["humidity"]    for r in window) / len(window)

        anomalies = []
        if temp is not None and (temp < -50 or temp > 50):
            anomalies.append({"sensor": addr, "type": "temperature", "value": temp, "timestamp": ts})
        if hum  is not None and (hum  <   0 or hum  > 100):
            anomalies.append({"sensor": addr, "type": "humidity",    "value": hum,  "timestamp": ts})

        level  = battery.drain()
        status = "RETURNING" if battery.is_low(threshold) else "OK"

        payload = {
            "average_temperature": avg_temp,
            "average_humidity":    avg_hum,
            "anomalies":           anomalies,
            "battery_level":       level,
            "status":              status,
            "timestamp":           datetime.now(timezone.utc).isoformat()
        }
        client.send(payload)

def main():
    args = drone_args()
    data_q = queue.Queue()

    # 1) TCP server for sensors
    threading.Thread(
        target=start_server,
        args=(args.host, args.port, data_q),
        daemon=True
    ).start()

    # 2) Processor + forward to Central
    client  = CentralClient(args.central_ip, args.central_port)
    battery = Battery(level=100.0, drain_rate=args.drain_rate)
    threading.Thread(
        target=processor_loop,
        args=(data_q, client, battery, args.battery_threshold),
        daemon=True
    ).start()

    # 3) Launch the Drone GUI (blocks)
    start_gui(data_q, battery)

if __name__ == "__main__":
    main()
