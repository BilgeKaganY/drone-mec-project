# drone/drone_client.py
import socket
import json
import time
import logging

class CentralClient:
    def __init__(self, ip: str, port: int, retry: float = 5.0):
        self.ip = ip
        self.port = port
        self.retry = retry
        self.sock = None

    def connect(self):
        while True:
            try:
                self.sock = socket.create_connection((self.ip, self.port))
                logging.info(f"Connected to Central Server at {self.ip}:{self.port}")
                return
            except Exception as e:
                logging.error(f"CentralServer connect failed: {e}. Retrying in {self.retry}s")
                time.sleep(self.retry)

    def send(self, payload: dict):
        """
        payload: a Python dict of your aggregated data,
                 e.g. {"avg_temp":..., "avg_hum":..., "anomalies":[...], "timestamp":...}
        """
        if self.sock is None:
            self.connect()
        data = json.dumps(payload) + "\n"
        try:
            self.sock.sendall(data.encode("utf-8"))
        except Exception as e:
            logging.error(f"Send to CentralServer failed: {e}. Reconnecting...")
            self.sock.close()
            self.sock = None
            self.connect()
            self.send(payload)
