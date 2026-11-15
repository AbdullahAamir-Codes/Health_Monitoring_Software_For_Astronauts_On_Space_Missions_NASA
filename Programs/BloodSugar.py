
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib.pyplot as plt

readings = []

def record_reading():
    try:
        glucose = float(glucose_entry.get())

        if glucose <= 0:
            status_label.config(
                text="Enter a valid glucose value",
                foreground="red"
            )
            return

        timestamp = datetime.now()

        readings.append((timestamp, glucose))

        if glucose < 4.0:
            status = "Low glucose"
            colour = "red"
        elif glucose <= 10.0:
            status = "Reading recorded"
            colour = "green"
        else:
            status = "High glucose"
            colour = "red"

        result_label.config(
            text=f"{glucose:.1f} mmol/L",
            foreground=colour
        )

        status_label.config(
            text=status,
            foreground=colour
        )

        history.insert(
            "",
            "end",
            values=(timestamp.strftime("%H:%M:%S"),
                    f"{glucose:.1f}",
                    status)
        )

        glucose_entry.delete(0, tk.END)

    except ValueError:
        status_label.config(
            text="Please enter a numeric value",
            foreground="red"
        )


def show_graph():
    if not readings:
        status_label.config(text="No readings available")
        return

    times = [r[0].strftime("%H:%M:%S") for r in readings]
    values = [r[1] for r in readings]

    plt.figure(figsize=(9, 5))
    plt.plot(times, values, marker="o")

    plt.title("Blood Glucose Monitoring")
    plt.xlabel("Time")
    plt.ylabel("Glucose (mmol/L)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


root = tk.Tk()
root.title("Astronaut Blood Glucose Monitor")
root.geometry("750x550")
root.configure(bg="#101827")

title = tk.Label(
    root,
    text="ASTRONAUT HEALTH MONITOR",
    font=("Arial", 20, "bold"),
    fg="white",
    bg="#101827"
)
title.pack(pady=20)

tk.Label(
    root,
    text="Blood Glucose Monitoring",
    font=("Arial", 15),
    fg="#38bdf8",
    bg="#101827"
).pack(pady=10)

glucose_entry = tk.Entry(
    root,
    font=("Arial", 16),
    justify="center"
)
glucose_entry.pack(pady=10)

glucose_entry.insert(0, "Enter mmol/L")

tk.Button(
    root,
    text="Record Reading",
    command=record_reading,
    bg="#2563eb",
    fg="white",
    font=("Arial", 12, "bold")
).pack(pady=10)

result_label = tk.Label(
    root,
    text="-- mmol/L",
    font=("Arial", 28, "bold"),
    fg="white",
    bg="#101827"
)
result_label.pack(pady=10)

status_label = tk.Label(
    root,
    text="Waiting for measurement",
    font=("Arial", 12),
    fg="white",
    bg="#101827"
)
status_label.pack(pady=5)

columns = ("Time", "Glucose (mmol/L)", "Status")

history = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=8
)

for col in columns:
    history.heading(col, text=col)
    history.column(col, width=200)

history.pack(pady=20, padx=20, fill="x")

tk.Button(
    root,
    text="View Glucose Graph",
    command=show_graph,
    bg="#059669",
    fg="white",
    font=("Arial", 12, "bold")
).pack(pady=10)

root.mainloop()