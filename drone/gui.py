#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue

def start_gui(data_q: queue.Queue, battery) -> None:
    """
    Very simple Drone GUI:
      - A scrolled text panel for raw sensor JSON.
      - A progress bar showing current battery.level.
    """
    root = tk.Tk()
    root.title("Drone Mobile Edge")

    # --- Raw sensor data panel ---
    raw_frame = ttk.LabelFrame(root, text="Incoming Sensor Data")
    raw_frame.pack(fill="both", expand=True, padx=5, pady=5)
    raw_text = scrolledtext.ScrolledText(raw_frame, height=10)
    raw_text.pack(fill="both", expand=True)

    # --- Battery panel ---
    batt_frame = ttk.Frame(root)
    batt_frame.pack(fill="x", padx=5, pady=5)
    ttk.Label(batt_frame, text="Battery Level:").pack(side="left")
    batt_bar = ttk.Progressbar(
        batt_frame,
        length=200,
        mode="determinate",
        maximum=100
    )
    batt_bar.pack(side="left", padx=5)

    # --- Periodic update function ---
    def update_gui():
        # 1) Update battery
        batt_bar["value"] = battery.level

        # 2) Drain any raw sensor messages from the queue
        try:
            while True:
                addr, text = data_q.get_nowait()
                raw_text.insert("end", f"{addr}: {text}\n")
                raw_text.see("end")
        except queue.Empty:
            pass

        # 3) Schedule next update
        root.after(500, update_gui)

    root.after(500, update_gui)
    root.mainloop()
