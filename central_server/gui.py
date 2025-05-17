#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext
import queue, json

def start_gui(display_q: queue.Queue):
    """
    Central Server GUI: table of aggregates and a scrolling log.
    """
    root = tk.Tk()
    root.title("Central Server Dashboard")

    # — Table of aggregates —
    cols = ("timestamp", "avg_temp", "avg_hum", "battery", "status", "anomalies")
    tree = ttk.Treeview(root, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=100, anchor="center")
    tree.pack(fill="both", expand=True, padx=5, pady=5)

    # — Log panel —
    log = scrolledtext.ScrolledText(root, height=10)
    log.pack(fill="both", expand=True, padx=5, pady=(0,5))

    def update():
        try:
            while True:
                rec = display_q.get_nowait()
                ts  = rec.get("timestamp", "")
                at  = f"{rec.get('average_temperature',0):.2f}"
                ah  = f"{rec.get('average_humidity',0):.2f}"
                bat = f"{rec.get('battery_level',0):.1f}"
                st  = rec.get("status","")
                an  = json.dumps(rec.get("anomalies", []))

                tree.insert("", "end", values=(ts, at, ah, bat, st, an))
                log.insert("end", f"{ts} Received: {rec}\n")
                log.see("end")
        except queue.Empty:
            pass
        root.after(500, update)

    root.after(500, update)
    root.mainloop()
