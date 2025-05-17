#!/usr/bin/env python3
import socket
import logging
import threading
import queue
import json
import threading
import logging
from logging.handlers import RotatingFileHandler
from central_server.gui import start_gui

from common.config import server_args

def handle_drone(conn, addr, display_q):
    logging.info(f"Drone connected from {addr}")
    buffer = b""
    try:
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                logging.info("Drone disconnected")
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                record = json.loads(line.decode().strip())
                logging.info(f"Received aggregate: {record}")
                display_q.put(record)
    finally:
        conn.close()

def main():
    args = server_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    # Rotating file handler
    fh = RotatingFileHandler("central.log", maxBytes=2_000_000, backupCount=5)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logging.getLogger().addHandler(fh)

    display_q = queue.Queue()
    threading.Thread(target=start_gui, args=(display_q,), daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((args.host, args.port))
        srv.listen()
        logging.info(f"Central Server listening on {args.host}:{args.port}")

        # (You can also start the GUI here by importing central_server.gui)
        while True:
            conn, addr = srv.accept()
            threading.Thread(
                target=handle_drone,
                args=(conn, addr, display_q),
                daemon=True
            ).start()

if __name__ == "__main__":
    main()
