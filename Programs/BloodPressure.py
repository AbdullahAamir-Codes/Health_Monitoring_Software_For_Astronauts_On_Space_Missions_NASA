
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates


# ==========================================
# CONFIGURATION
# ==========================================

DB_FILE = Path(__file__).with_name("blood_pressure.db")

LOW_SYS = 90
LOW_DIA = 60

HIGH_SYS = 135
HIGH_DIA = 85


# ==========================================
# DATABASE
# ==========================================

def connect_db():
    return sqlite3.connect(DB_FILE)


def create_database():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                systolic INTEGER NOT NULL,
                diastolic INTEGER NOT NULL,
                category TEXT NOT NULL,
                notes TEXT,
                recorded_at TEXT NOT NULL
            )
        """)


# ==========================================
# BLOOD PRESSURE CLASSIFICATION
# ==========================================

def classify_pressure(systolic, diastolic):

    if systolic < LOW_SYS or diastolic < LOW_DIA:
        return "Low"

    elif systolic >= HIGH_SYS or diastolic >= HIGH_DIA:
        return "High"

    return "Normal"


# ==========================================
# MAIN APPLICATION
# ==========================================

class BloodPressureTracker:

    def __init__(self, root):

        self.root = root
        self.root.title("Blood Pressure Monitoring System")
        self.root.geometry("1150x780")
        self.root.minsize(950, 680)

        self.root.configure(bg="#f1f5f9")

        create_database()

        self.setup_style()
        self.create_interface()

        self.refresh_all()

    # --------------------------------------
    # STYLING
    # --------------------------------------

    def setup_style(self):

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "Treeview",
            rowheight=30,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

        style.configure(
            "TNotebook.Tab",
            padding=[15, 8],
            font=("Arial", 10, "bold")
        )

    # --------------------------------------
    # MAIN INTERFACE
    # --------------------------------------

    def create_interface(self):

        header = tk.Frame(
            self.root,
            bg="#172554",
            height=100
        )

        header.pack(fill="x")

        tk.Label(
            header,
            text="BLOOD PRESSURE MONITOR",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#172554"
        ).pack(pady=(18, 4))

        tk.Label(
            header,
            text="Manual Health Tracking & Weekly Analysis",
            font=("Arial", 10),
            fg="#bfdbfe",
            bg="#172554"
        ).pack()

        # Notebook tabs

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.entry_tab = tk.Frame(
            self.notebook,
            bg="#f1f5f9"
        )

        self.history_tab = tk.Frame(
            self.notebook,
            bg="#f1f5f9"
        )

        self.graph_tab = tk.Frame(
            self.notebook,
            bg="#f1f5f9"
        )

        self.notebook.add(
            self.entry_tab,
            text="Add Reading"
        )

        self.notebook.add(
            self.history_tab,
            text="History"
        )

        self.notebook.add(
            self.graph_tab,
            text="Weekly Graph"
        )

        self.create_entry_tab()
        self.create_history_tab()
        self.create_graph_tab()

    # --------------------------------------
    # ENTRY TAB
    # --------------------------------------

    def create_entry_tab(self):

        container = tk.Frame(
            self.entry_tab,
            bg="#f1f5f9"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        tk.Label(
            container,
            text="Enter Blood Pressure Reading",
            font=("Arial", 18, "bold"),
            bg="#f1f5f9",
            fg="#172554"
        ).pack(anchor="w", pady=(0, 20))

        input_frame = tk.Frame(
            container,
            bg="white",
            padx=25,
            pady=20
        )

        input_frame.pack(fill="x")

        # Systolic

        tk.Label(
            input_frame,
            text="Systolic Pressure (SYS)",
            font=("Arial", 11, "bold"),
            bg="white"
        ).grid(row=0, column=0, sticky="w", pady=8)

        self.systolic_entry = ttk.Entry(
            input_frame,
            font=("Arial", 13),
            width=20
        )

        self.systolic_entry.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 15)
        )

        # Diastolic

        tk.Label(
            input_frame,
            text="Diastolic Pressure (DIA)",
            font=("Arial", 11, "bold"),
            bg="white"
        ).grid(row=2, column=0, sticky="w", pady=8)

        self.diastolic_entry = ttk.Entry(
            input_frame,
            font=("Arial", 13),
            width=20
        )

        self.diastolic_entry.grid(
            row=3,
            column=0,
            sticky="w",
            pady=(0, 15)
        )

        # Notes

        tk.Label(
            input_frame,
            text="Notes (Optional)",
            font=("Arial", 11, "bold"),
            bg="white"
        ).grid(row=4, column=0, sticky="w", pady=8)

        self.notes_entry = ttk.Entry(
            input_frame,
            font=("Arial", 11),
            width=45
        )

        self.notes_entry.grid(
            row=5,
            column=0,
            sticky="w",
            pady=(0, 15)
        )

        # Add button

        tk.Button(
            input_frame,
            text="SAVE READING",
            font=("Arial", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.save_reading
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=10
        )

        # Result panel

        self.result_frame = tk.Frame(
            container,
            bg="white",
            padx=20,
            pady=20
        )

        self.result_frame.pack(
            fill="x",
            pady=20
        )

        self.result_label = tk.Label(
            self.result_frame,
            text="Your latest reading will appear here.",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#64748b"
        )

        self.result_label.pack(anchor="w")

        self.advice_label = tk.Label(
            self.result_frame,
            text="",
            font=("Arial", 10),
            bg="white",
            fg="#475569",
            wraplength=850,
            justify="left"
        )

        self.advice_label.pack(
            anchor="w",
            pady=(10, 0)
        )

        # Statistics

        stats_frame = tk.Frame(
            container,
            bg="#f1f5f9"
        )

        stats_frame.pack(fill="x")

        self.total_label = self.create_stat_card(
            stats_frame,
            "TOTAL READINGS",
            "0"
        )

        self.average_label = self.create_stat_card(
            stats_frame,
            "AVERAGE BP",
            "--/--"
        )

        self.latest_label = self.create_stat_card(
            stats_frame,
            "LATEST READING",
            "--/--"
        )

    def create_stat_card(self, parent, heading, initial):

        card = tk.Frame(
            parent,
            bg="white",
            padx=20,
            pady=15,
            highlightbackground="#e2e8f0",
            highlightthickness=1
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=heading,
            bg="white",
            fg="#64748b",
            font=("Arial", 9, "bold")
        ).pack()

        value = tk.Label(
            card,
            text=initial,
            bg="white",
            fg="#172554",
            font=("Arial", 19, "bold")
        )

        value.pack(pady=5)

        return value

    # --------------------------------------
    # SAVE READING
    # --------------------------------------

    def save_reading(self):

        try:
            systolic = int(self.systolic_entry.get())
            diastolic = int(self.diastolic_entry.get())

        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid whole numbers."
            )
            return

        if not (50 <= systolic <= 300):
            messagebox.showerror(
                "Invalid Input",
                "Systolic must be between 50 and 300."
            )
            return

        if not (30 <= diastolic <= 200):
            messagebox.showerror(
                "Invalid Input",
                "Diastolic must be between 30 and 200."
            )
            return

        if systolic <= diastolic:
            messagebox.showerror(
                "Invalid Reading",
                "Systolic must be higher than diastolic."
            )
            return

        category = classify_pressure(
            systolic,
            diastolic
        )

        notes = self.notes_entry.get().strip()

        recorded_at = datetime.now().isoformat(
            timespec="seconds"
        )

        with connect_db() as conn:

            conn.execute("""
                INSERT INTO readings
                (systolic, diastolic, category, notes, recorded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                systolic,
                diastolic,
                category,
                notes,
                recorded_at
            ))

        self.systolic_entry.delete(0, tk.END)
        self.diastolic_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

        self.show_result(
            systolic,
            diastolic,
            category
        )

        self.refresh_all()

        if systolic >= 180 or diastolic >= 120:

            messagebox.showwarning(
                "Very High Reading",
                "Your reading is extremely high.\n\n"
                "Sit quietly and repeat the measurement "
                "after 5 minutes.\n\n"
                "If it remains this high, seek urgent "
                "same-day medical advice."
            )

    # --------------------------------------
    # DISPLAY RESULT
    # --------------------------------------

    def show_result(
        self,
        systolic,
        diastolic,
        category
    ):

        colors = {
            "Low": "#2563eb",
            "Normal": "#15803d",
            "High": "#dc2626"
        }

        messages = {
            "Low": (
                "Your reading is below the usual "
                "low blood pressure threshold. "
                "If you experience dizziness or fainting, "
                "contact your GP."
            ),

            "Normal": (
                "Your reading is below the usual "
                "high blood pressure threshold for "
                "home measurements."
            ),

            "High": (
                "Your reading is above the usual "
                "high blood pressure threshold for "
                "home measurements. Repeat measurements "
                "and discuss consistently high readings "
                "with your GP."
            )
        }

        self.result_label.config(
            text=f"{category.upper()} BLOOD PRESSURE  |  "
                 f"{systolic}/{diastolic} mmHg",
            fg=colors[category]
        )

        self.advice_label.config(
            text=messages[category]
        )

    # --------------------------------------
    # HISTORY TAB
    # --------------------------------------

    def create_history_tab(self):

        container = tk.Frame(
            self.history_tab,
            bg="#f1f5f9"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        tk.Label(
            container,
            text="Blood Pressure History",
            font=("Arial", 17, "bold"),
            bg="#f1f5f9",
            fg="#172554"
        ).pack(anchor="w", pady=(0, 15))

        columns = (
            "id",
            "date",
            "systolic",
            "diastolic",
            "category",
            "notes"
        )

        self.history_tree = ttk.Treeview(
            container,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": "ID",
            "date": "Date & Time",
            "systolic": "Systolic",
            "diastolic": "Diastolic",
            "category": "Category",
            "notes": "Notes"
        }

        for col in columns:

            self.history_tree.heading(
                col,
                text=headings[col]
            )

        self.history_tree.column("id", width=50)
        self.history_tree.column("date", width=160)
        self.history_tree.column("systolic", width=100)
        self.history_tree.column("diastolic", width=100)
        self.history_tree.column("category", width=100)
        self.history_tree.column("notes", width=300)

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.history_tree.yview
        )

        self.history_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.history_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        tk.Button(
            self.history_tab,
            text="DELETE SELECTED READING",
            bg="#dc2626",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=8,
            command=self.delete_reading
        ).pack(pady=10)

    # --------------------------------------
    # LOAD HISTORY
    # --------------------------------------

    def load_history(self):

        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        with connect_db() as conn:

            rows = conn.execute("""
                SELECT id, recorded_at, systolic,
                       diastolic, category, notes
                FROM readings
                ORDER BY recorded_at DESC
            """).fetchall()

        for row in rows:

            recorded = datetime.fromisoformat(
                row[1]
            ).strftime("%d/%m/%Y %H:%M")

            self.history_tree.insert(
                "",
                tk.END,
                values=(
                    row[0],
                    recorded,
                    row[2],
                    row[3],
                    row[4],
                    row[5]
                )
            )

    # --------------------------------------
    # DELETE READING
    # --------------------------------------

    def delete_reading(self):

        selected = self.history_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Select Reading",
                "Please select a reading to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this reading?"
        ):
            return

        for item in selected:

            reading_id = self.history_tree.item(
                item,
                "values"
            )[0]

            with connect_db() as conn:
                conn.execute(
                    "DELETE FROM readings WHERE id = ?",
                    (reading_id,)
                )

        self.refresh_all()

    # --------------------------------------
    # WEEKLY GRAPH TAB
    # --------------------------------------

    def create_graph_tab(self):

        container = tk.Frame(
            self.graph_tab,
            bg="#f1f5f9"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        tk.Label(
            container,
            text="Weekly Blood Pressure Analysis",
            font=("Arial", 17, "bold"),
            bg="#f1f5f9",
            fg="#172554"
        ).pack(anchor="w")

        tk.Label(
            container,
            text="Showing individual readings from the last 7 days",
            font=("Arial", 10),
            bg="#f1f5f9",
            fg="#64748b"
        ).pack(anchor="w", pady=(5, 10))

        self.figure = Figure(
            figsize=(9, 5),
            dpi=100,
            facecolor="white"
        )

        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=container
        )

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        tk.Button(
            container,
            text="REFRESH GRAPH",
            bg="#2563eb",
            fg="white",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=8,
            command=self.update_graph
        ).pack(pady=10)

    # --------------------------------------
    # UPDATE WEEKLY GRAPH
    # --------------------------------------

    def update_graph(self):

        self.ax.clear()

        start_date = (
            datetime.now() - timedelta(days=7)
        )

        with connect_db() as conn:

            rows = conn.execute("""
                SELECT systolic, diastolic, recorded_at
                FROM readings
                WHERE recorded_at >= ?
                ORDER BY recorded_at ASC
            """, (
                start_date.isoformat(timespec="seconds"),
            )).fetchall()

        if not rows:

            self.ax.text(
                0.5,
                0.5,
                "No readings recorded in the last 7 days",
                ha="center",
                va="center",
                transform=self.ax.transAxes,
                fontsize=12
            )

            self.ax.set_axis_off()

        else:

            dates = [
                datetime.fromisoformat(row[2])
                for row in rows
            ]

            systolic = [row[0] for row in rows]
            diastolic = [row[1] for row in rows]

            self.ax.plot(
                dates,
                systolic,
                marker="o",
                linewidth=2,
                label="Systolic (SYS)"
            )

            self.ax.plot(
                dates,
                diastolic,
                marker="o",
                linewidth=2,
                label="Diastolic (DIA)"
            )

            self.ax.axhline(
                135,
                linestyle="--",
                alpha=0.6,
                label="Home systolic high threshold (135)"
            )

            self.ax.axhline(
                85,
                linestyle=":",
                alpha=0.6,
                label="Home diastolic high threshold (85)"
            )

            self.ax.set_ylabel(
                "Blood Pressure (mmHg)"
            )

            self.ax.set_xlabel(
                "Date and Time"
            )

            self.ax.xaxis.set_major_formatter(
                mdates.DateFormatter("%d %b %H:%M")
            )

            self.ax.tick_params(
                axis="x",
                rotation=35
            )

            self.ax.legend(
                loc="upper left",
                fontsize=8
            )

            self.ax.grid(
                True,
                alpha=0.25
            )

            self.ax.set_axis_on()

        self.figure.tight_layout()
        self.canvas.draw()

    # --------------------------------------
    # STATISTICS
    # --------------------------------------

    def update_statistics(self):

        with connect_db() as conn:

            total = conn.execute(
                "SELECT COUNT(*) FROM readings"
            ).fetchone()[0]

            latest = conn.execute("""
                SELECT systolic, diastolic
                FROM readings
                ORDER BY recorded_at DESC, id DESC
                LIMIT 1
            """).fetchone()

            average = conn.execute("""
                SELECT AVG(systolic), AVG(diastolic)
                FROM readings
            """).fetchone()

        self.total_label.config(
            text=str(total)
        )

        if latest:

            self.latest_label.config(
                text=f"{latest[0]}/{latest[1]}"
            )

            self.average_label.config(
                text=f"{average[0]:.0f}/{average[1]:.0f}"
            )

        else:

            self.latest_label.config(text="--/--")
            self.average_label.config(text="--/--")

    # --------------------------------------
    # REFRESH EVERYTHING
    # --------------------------------------

    def refresh_all(self):

        self.load_history()
        self.update_statistics()
        self.update_graph()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BloodPressureTracker(root)

    root.mainloop()