#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue, json
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def start_gui(data_q: queue.Queue, battery, threshold: float):
    """
    Drone GUI: live plots, anomalies list, battery status,
    manual drain slider and Recharge button.
    """
    root = tk.Tk()
    root.title("Drone Mobile Edge Dashboard")

    # — Top: Status, Battery, Controls —
    top = ttk.Frame(root)
    top.pack(fill="x", padx=5, pady=5)

    status_var = tk.StringVar(value="OK")
    ttk.Label(top, text="Status:").pack(side="left")
    status_lbl = ttk.Label(top, textvariable=status_var, font=("TkDefaultFont", 12, "bold"))
    status_lbl.pack(side="left", padx=(0,20))

    ttk.Label(top, text="Battery:").pack(side="left")
    batt_bar = ttk.Progressbar(top, length=150, maximum=100)
    batt_bar.pack(side="left", padx=(0,20))

    ttk.Label(top, text="Manual Drain Rate:").pack(side="left")
    drain_slider = ttk.Scale(top, from_=0, to=5, orient="horizontal")
    drain_slider.set(1.0)
    drain_slider.pack(side="left", fill="x", expand=True, padx=(0,20))

    def do_recharge():
        battery.recharge(25)  # recharge 25%
    ttk.Button(top, text="Recharge +25%", command=do_recharge).pack(side="left")

    # — Middle: Temperature/Humidity Plots —
    plot_frame = ttk.LabelFrame(root, text="Temperature & Humidity Over Time")
    plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

    fig = Figure(figsize=(6,3))
    ax_temp = fig.add_subplot(211)
    ax_hum  = fig.add_subplot(212)
    ax_temp.set_ylabel("°C")
    ax_hum.set_ylabel("%")
    ax_hum.set_xlabel("Seconds since start")

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # — Bottom: Anomalies & Event Log —
    bottom = ttk.Frame(root)
    bottom.pack(fill="both", expand=True, padx=5, pady=5)

    anom_frame = ttk.LabelFrame(bottom, text="Anomalies")
    anom_frame.pack(side="left", fill="both", expand=True, padx=(0,5))
    anom_list = tk.Listbox(anom_frame)
    anom_list.pack(fill="both", expand=True)

    log_frame = ttk.LabelFrame(bottom, text="Event Log")
    log_frame.pack(side="left", fill="both", expand=True)
    log_text = scrolledtext.ScrolledText(log_frame, height=10)
    log_text.pack(fill="both", expand=True)

    # — Data buffers —
    times, temps, hums = [], [], []
    start_time = None

    def update():
        nonlocal start_time
        # 1) Update drain rate and drain battery
        battery.drain_rate = drain_slider.get()
        lvl = battery.drain()
        batt_bar["value"] = lvl

        # 2) Pull all queued sensor messages
        try:
            while True:
                addr, raw = data_q.get_nowait()
                rec = json.loads(raw)
                ts  = datetime.fromisoformat(rec["timestamp"]).timestamp()
                if start_time is None:
                    start_time = ts
                rel = ts - start_time
                times.append(rel)
                temps.append(rec["temperature"])
                hums.append(rec["humidity"])

                # 3) Anomaly list
                if (rec["temperature"] < -50 or rec["temperature"] > 50
                 or rec["humidity"] < 0   or rec["humidity"] > 100):
                    anom_list.insert(
                        "end",
                        f"{addr} @ {rec['timestamp']}: T={rec['temperature']} H={rec['humidity']}"
                    )
                    anom_list.see("end")

                # 4) Event log
                log_text.insert("end", f"{addr} {raw}\n")
                log_text.see("end")
        except queue.Empty:
            pass

        # 5) Redraw plots
        ax_temp.clear(); ax_hum.clear()
        ax_temp.plot(times, temps)
        ax_hum.plot(times, hums)
        ax_temp.set_ylabel("°C"); ax_hum.set_ylabel("%")
        ax_hum.set_xlabel("Seconds since start")
        canvas.draw()

        # 6) Status banner color
        if lvl <= threshold:
            status_var.set("RETURNING TO BASE")
            status_lbl.configure(foreground="red")
        else:
            status_var.set("OK")
            status_lbl.configure(foreground="green")

        root.after(500, update)

    root.after(500, update)
    root.mainloop()
