# central_server/gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import json

def start_gui(display_q):
    root = tk.Tk()
    root.title("Central Server GUI")

    # Table for aggregates
    cols = ("timestamp", "avg_temp", "avg_hum", "anomalies")
    tree = ttk.Treeview(root, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
    tree.pack(fill="both", expand=True)

    # Log panel
    log = scrolledtext.ScrolledText(root, height=10)
    log.pack(fill="both", expand=True)

    def update_loop():
        try:
            while True:
                record = display_q.get_nowait()
                ts = record.get("timestamp", "")
                at = record.get("average_temperature", "")
                ah = record.get("average_humidity", "")
                an = json.dumps(record.get("anomalies", []))
                tree.insert("", "end", values=(ts, at, ah, an))
                log.insert("end", f"{ts} Received: {record}\n")
        except:
            pass
        root.after(500, update_loop)

    root.after(500, update_loop)
    root.mainloop()
