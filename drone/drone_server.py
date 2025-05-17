#!/usr/bin/env python3
import socket
import logging
import threading

def handle_sensor(conn, addr, data_q):
    logging.info(f"Handler for {addr} started")
    buffer = b""
    try:
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                logging.info(f"Sensor {addr} disconnected")
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                text = line.decode().strip()
                logging.info(f"[{addr}] {text}")
                data_q.put((addr, text))
    except Exception as e:
        logging.error(f"Error in handler {addr}: {e}")
    finally:
        conn.close()

def start_server(host: str, port: int, data_q):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen()
    logging.info(f"Drone server listening on {host}:{port}")

    while True:
        conn, addr = srv.accept()
        logging.info(f"New sensor connected from {addr}")
        t = threading.Thread(
            target=handle_sensor,
            args=(conn, addr, data_q),
            daemon=True
        )
        t.start()
