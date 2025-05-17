# common/config.py
import argparse

def sensor_args():
    p = argparse.ArgumentParser("Headless Sensor Node")
    p.add_argument("--drone_ip",   required=True)
    p.add_argument("--drone_port", type=int, required=True)
    p.add_argument("--interval",   type=float, default=2.0,
                   help="Seconds between readings")
    p.add_argument("--retry",      type=float, default=5.0,
                   help="Seconds before reconnect attempt")
    p.add_argument("--id",         default="sensor1",
                   help="Unique sensor ID")
    return p.parse_args()

def drone_args():
    p = argparse.ArgumentParser("Drone Edge")
    p.add_argument("--host",            default="0.0.0.0",
                   help="IP to bind sensor‐server on")
    p.add_argument("--port",            type=int, default=5000,
                   help="Port to bind sensor‐server on")
    p.add_argument("--central_ip",      default="127.0.0.1",
                   help="IP of Central Server")
    p.add_argument("--central_port",    type=int, default=6000,
                   help="Port to bind Central Server")
    p.add_argument("--battery_threshold", type=float, default=20.0,
                   help="Level (%) below which drone returns to base")
    p.add_argument("--drain_rate",      type=float, default=1.0,
                   help="Battery % drained per second")
    return p.parse_args()

def server_args():
    p = argparse.ArgumentParser("Central Server")
    p.add_argument("--host", default="0.0.0.0",
                   help="IP to bind on")
    p.add_argument("--port", type=int, default=6000,
                   help="Port to bind on")
    return p.parse_args()
