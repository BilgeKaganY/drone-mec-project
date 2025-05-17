#!/usr/bin/env python3
import threading
import queue
import json
import collections
import logging
from datetime import datetime, timezone

from common.config      import drone_args
from drone.battery      import Battery
from drone.drone_client import CentralClient
from drone.drone_server import start_server
from drone.gui          import start_gui

def processor_loop(data_q, client: CentralClient, battery: Battery, threshold: float):
    # Rolling window of last 10 readings
    window = collections.deque(maxlen=10)

    # Option B: buffer aggregates when battery is low
    in_return_mode   = False
    queued_payloads = []

    while True:
        addr, text = data_q.get()  # raw from sensor handlers
        reading    = json.loads(text)
        temp       = reading.get("temperature")
        hum        = reading.get("humidity")
        ts         = reading.get("timestamp")

        # 1) Update rolling window
        window.append(reading)
        avg_temp = sum(r["temperature"] for r in window) / len(window)
        avg_hum  = sum(r["humidity"]    for r in window) / len(window)

        # 2) Detect anomalies
        anomalies = []
        if temp is not None and (temp < -50 or temp > 50):
            anomalies.append({"sensor": addr, "type": "temperature", "value": temp, "timestamp": ts})
        if hum  is not None and (hum  <   0 or hum  > 100):
            anomalies.append({"sensor": addr, "type": "humidity",    "value": hum,  "timestamp": ts})

        # 3) Drain battery and check threshold
        level = battery.drain()
        if level <= threshold and not in_return_mode:
            logging.warning("Battery low—entering RETURN-TO-BASE (queuing mode)")
            in_return_mode = True

        # 4) Build payload
        payload = {
            "average_temperature": avg_temp,
            "average_humidity":    avg_hum,
            "anomalies":           anomalies,
            "battery_level":       level,
            "status":              ("RETURNING" if in_return_mode else "OK"),
            "timestamp":           datetime.now(timezone.utc).isoformat()
        }

        # 5) Either queue or send
        if in_return_mode:
            queued_payloads.append(payload)
        else:
            client.send(payload)

        # 6) If recharged above threshold, flush queue
        if in_return_mode and battery.level > threshold:
            logging.info("Battery restored—exiting RETURN-TO-BASE and flushing queue")
            in_return_mode = False
            for p in queued_payloads:
                client.send(p)
            queued_payloads.clear()

def main():
    # Basic logging for warnings/info
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    args   = drone_args()
    data_q = queue.Queue()

    # 1) Start the TCP server (sensor accept + handlers)
    threading.Thread(
        target=start_server,
        args=(args.host, args.port, data_q),
        daemon=True
    ).start()

    # 2) Start the processor that aggregates & forwards (or queues)
    client  = CentralClient(args.central_ip, args.central_port)
    battery = Battery(level=100.0, drain_rate=args.drain_rate)
    threading.Thread(
        target=processor_loop,
        args=(data_q, client, battery, args.battery_threshold),
        daemon=True
    ).start()

    # 3) Finally launch the GUI (blocks here)
    start_gui(data_q, battery, args.battery_threshold)

if __name__ == "__main__":
    main()
