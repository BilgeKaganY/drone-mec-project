# common/config.py
import argparse
import configparser
import os

# Load config.ini if it exists
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(os.getcwd(), "config.ini"))

def sensor_args():
    defaults = _cfg["sensor"] if "sensor" in _cfg else {}
    p = argparse.ArgumentParser("Headless Sensor Node")
    p.add_argument("--drone_ip",
        default=defaults.get("drone_ip"),
        required="drone_ip" not in defaults)
    p.add_argument("--drone_port",
        type=int,
        default=defaults.get("drone_port"),
        required="drone_port" not in defaults)
    p.add_argument("--interval",
        type=float,
        default=defaults.get("interval", 2.0))
    p.add_argument("--retry",
        type=float,
        default=defaults.get("retry", 5.0))
    p.add_argument("--id",
        default=defaults.get("id", "sensor1"))
    return p.parse_args()

def drone_args():
    defaults = _cfg["drone"] if "drone" in _cfg else {}
    p = argparse.ArgumentParser("Drone Edge")
    p.add_argument("--host",
        default=defaults.get("host", "0.0.0.0"))
    p.add_argument("--port",
        type=int,
        default=defaults.get("port", 5000))
    p.add_argument("--central_ip",
        default=defaults.get("central_ip", "127.0.0.1"))
    p.add_argument("--central_port",
        type=int,
        default=defaults.get("central_port", 6000))
    p.add_argument("--battery_threshold",
        type=float,
        default=defaults.get("battery_threshold", 20.0))
    p.add_argument("--drain_rate",
        type=float,
        default=defaults.get("drain_rate", 1.0))
    return p.parse_args()

def server_args():
    defaults = _cfg["central"] if "central" in _cfg else {}
    p = argparse.ArgumentParser("Central Server")
    p.add_argument("--host",
        default=defaults.get("host", "0.0.0.0"))
    p.add_argument("--port",
        type=int,
        default=defaults.get("port", 6000))
    return p.parse_args()   
