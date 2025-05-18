#!/usr/bin/env python3
import subprocess, time, os, sys, signal

# Commands for your components
CENTRAL = ["python", "-m", "central_server.central_server"]
DRONE   = ["python", "-m", "drone.main"]
S1      = ["python", "-m", "sensors.sensor", "--id", "sensor1"]
S2      = ["python", "-m", "sensors.sensor", "--id", "sensor2"]

LOGS = {
    "central": "central.log",
    "drone":   "drone.log",
}

def kill_all(procs):
    for p in procs:
        try:
            p.send_signal(signal.SIGINT)
            p.wait(2)
        except:
            pass

def read(path):
    with open(path, "r") as f:
        return f.read()

def test_normal_flow():
    # start central, drone, 2 sensors
    p_c = subprocess.Popen(CENTRAL)
    time.sleep(1)
    p_d = subprocess.Popen(DRONE)
    time.sleep(1)
    p1 = subprocess.Popen(S1)
    p2 = subprocess.Popen(S2)
    time.sleep(5)
    log = read(LOGS["central"])
    ok = "average_temperature" in log
    kill_all([p1,p2,p_d,p_c])
    return ok

def test_sensor_reconnect():
    p_c = subprocess.Popen(CENTRAL); time.sleep(1)
    p_d = subprocess.Popen(DRONE);   time.sleep(1)
    p1 = subprocess.Popen(S1);       time.sleep(2)
    p2 = subprocess.Popen(S2);       time.sleep(2)

    # kill and restart sensor1
    p1.send_signal(signal.SIGINT); p1.wait(); time.sleep(2)
    p1b = subprocess.Popen(S1);    time.sleep(2)

    log = read(LOGS["drone"])
    ok = "disconnected" in log and "New sensor connected" in log
    kill_all([p1b,p2,p_d,p_c])
    return ok

def test_low_battery_queue():
    # start drone with high threshold so it queues immediately
    p_c = subprocess.Popen(CENTRAL); time.sleep(1)
    p_d = subprocess.Popen(DRONE + ["--battery_threshold","100","--drain_rate","0"])
    time.sleep(1)
    p1 = subprocess.Popen(S1); p2 = subprocess.Popen(S2)
    time.sleep(3)
    # central.log should be empty
    open(LOGS["central"],"w").close()
    time.sleep(3)
    mid = read(LOGS["central"]).strip()
    if mid != "":
        kill_all([p1,p2,p_d,p_c])
        return False
    # now restart drone at 0% threshold to flush
    p_d.send_signal(signal.SIGINT); p_d.wait()
    p_d2 = subprocess.Popen(DRONE + ["--battery_threshold","0"])
    time.sleep(3)
    post = read(LOGS["central"])
    ok = "average_temperature" in post
    kill_all([p1,p2,p_d2,p_c])
    return ok

def test_anomaly_injection():
    p_c = subprocess.Popen(CENTRAL); time.sleep(1)
    p_d = subprocess.Popen(DRONE);   time.sleep(1)
    p1 = subprocess.Popen(S1);       time.sleep(1)
    p2 = subprocess.Popen(S2);       time.sleep(1)

    # inject a bad packet directly
    bad = b'{"sensor_id":"x","temperature":1000,"humidity":50,"timestamp":"2025-05-18T00:00:00Z"}\n'
    subprocess.run(["nc","127.0.0.1","5000"], input=bad)
    time.sleep(2)

    dlog = read(LOGS["drone"])
    clog = read(LOGS["central"])
    ok = "1000" in dlog and "1000" in clog

    kill_all([p1,p2,p_d,p_c])
    return ok

if __name__=="__main__":
    tests = [
        ("Normal flow", test_normal_flow),
        ("Sensor reconnect", test_sensor_reconnect),
        ("Low-battery queue", test_low_battery_queue),
        ("Anomaly injection", test_anomaly_injection),
    ]
    failures = 0
    for name, fn in tests:
        print(f"==> {name} ... ", end="", flush=True)
        if fn():
            print("PASS")
        else:
            print("FAIL")
            failures += 1
    sys.exit(failures)
