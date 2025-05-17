# common/protocols.py
import json
from datetime import datetime, timezone

def make_sensor_payload(sensor_id: str, temperature: float, humidity: float) -> bytes:
    payload = {
        "sensor_id": sensor_id,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    # We’ll send each JSON terminated by newline for easy framing
    return (json.dumps(payload) + "\n").encode("utf-8")
