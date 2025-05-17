#!/usr/bin/env python3
import logging
import random
import socket
import time
import logging
from logging.handlers import RotatingFileHandler

from common.config   import sensor_args
from common.protocols import make_sensor_payload

def setup_logging(sensor_id):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(f"%(asctime)s [%(levelname)s] [{sensor_id}] %(message)s")
    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    # File
    fh = RotatingFileHandler(f"sensor_{sensor_id}.log",
                             maxBytes=1_000_000,
                             backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

def connect_with_retry(ip, port, retry_interval):
    while True:
        try:
            sock = socket.create_connection((ip, port))
            logging.info(f"Connected to Drone at {ip}:{port}")
            return sock
        except Exception as e:
            logging.error(f"Connection failed: {e}. Retrying in {retry_interval}s.")
            time.sleep(retry_interval)

def main():
    args = sensor_args()
    setup_logging(args.id)

    sock = connect_with_retry(args.drone_ip, args.drone_port, args.retry)
    while True:
        temp = round(20 + 10 * random.random(), 2)
        hum  = round(30 + 50 * random.random(), 2)

        payload = make_sensor_payload(args.id, temp, hum)
        try:
            sock.sendall(payload)
            logging.info(f"Sent: temp={temp}°C, hum={hum}%")
        except Exception as e:
            logging.error(f"Send failed: {e}. Reconnecting...")
            sock.close()
            sock = connect_with_retry(args.drone_ip, args.drone_port, args.retry)
            continue

        time.sleep(args.interval)

if __name__ == "__main__":
    main()
