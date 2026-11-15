# Age detection and gender detection models are taken from GitHub
# https://github.com/sailinishavempali/Gender-and-Age-Detection.git

import cv2
import numpy as np
import time
import tkinter as tk

from tkinter import messagebox
from collections import deque
from pathlib import Path
from PIL import Image, ImageTk

from scipy.signal import butter, sosfiltfilt, periodogram

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CAMERA_INDEX = 0

SAMPLE_RATE = 30
WINDOW_SECONDS = 12
MINIMUM_SECONDS = 8

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

AGE_MODEL = MODEL_DIR / "age_net.caffemodel"
AGE_CONFIG = MODEL_DIR / "age_deploy.prototxt"

GENDER_MODEL = MODEL_DIR / "gender_net.caffemodel"
GENDER_CONFIG = MODEL_DIR / "gender_deploy.prototxt"

AGE_LABELS = [
    "(0-2)", "(4-6)", "(8-12)", "(15-20)",
    "(25-32)", "(38-43)", "(48-53)", "(60-100)"
]

GENDER_LABELS = ["Male", "Female"]

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)

def get_age_heart_range(age_group):

    if age_group is None:
        return 60, 100

    age_midpoints = {
        "(0-2)": 1,
        "(4-6)": 5,
        "(8-12)": 10,
        "(15-20)": 18,
        "(25-32)": 28,
        "(38-43)": 40,
        "(48-53)": 50,
        "(60-100)": 70
    }

    age = age_midpoints.get(age_group, 28)

    if age < 1:
        return 100, 160
    elif age < 3:
        return 90, 150
    elif age < 6:
        return 80, 140
    elif age < 13:
        return 70, 120
    else:
        return 60, 100


def classify_heartbeat(bpm, age_group):

    lower, upper = get_age_heart_range(age_group)

    if bpm < lower:
        return "SLOW", "blue"

    elif bpm <= upper:
        return "NORMAL", "green"

    elif bpm <= upper + 20:
        return "FAST", "orange"

    else:
        return "TOO FAST", "red"

class HeartbeatMonitor:

    def __init__(self):

        self.timestamps = deque(
            maxlen=WINDOW_SECONDS * SAMPLE_RATE
        )

        self.green_values = deque(
            maxlen=WINDOW_SECONDS * SAMPLE_RATE
        )

        self.bpm = None
        self.filtered_signal = None
        self.signal_quality = "Waiting for finger..."

        self.last_calculation = 0

    def reset(self):

        self.timestamps.clear()
        self.green_values.clear()

        self.bpm = None
        self.filtered_signal = None

        self.signal_quality = "Waiting for finger..."

    def add_sample(self, frame):

        height, width = frame.shape[:2]

        # Central fingertip measurement region
        x1 = int(width * 0.35)
        x2 = int(width * 0.65)

        y1 = int(height * 0.35)
        y2 = int(height * 0.65)

        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:
            return None

        # Green channel is useful for camera-based PPG
        green_channel = roi[:, :, 1]

        green_mean = float(np.mean(green_channel))

        timestamp = time.monotonic()

        self.timestamps.append(timestamp)
        self.green_values.append(green_mean)

        # Calculate heartbeat every second
        if timestamp - self.last_calculation >= 1:

            self.last_calculation = timestamp

            return self.calculate_bpm()

        return self.bpm

    def calculate_bpm(self):

        if len(self.green_values) < SAMPLE_RATE * MINIMUM_SECONDS:

            self.signal_quality = "Collecting signal..."
            return None

        values = np.array(self.green_values, dtype=float)

        times = np.array(self.timestamps, dtype=float)

        duration = times[-1] - times[0]

        if duration < MINIMUM_SECONDS:
            return None

        # Remove the average brightness
        values = values - np.mean(values)

        # Check whether the camera is detecting any variation
        if np.std(values) < 0.15:

            self.signal_quality = "Weak signal - adjust finger"
            self.bpm = None

            return None

        # Bandpass filter: 0.7 Hz to 3.5 Hz
        # Corresponds to approximately 42-210 BPM
        try:

            sos = butter(
                3,
                [0.7, 3.5],
                btype="bandpass",
                fs=SAMPLE_RATE,
                output="sos"
            )

            filtered = sosfiltfilt(sos, values)

            self.filtered_signal = filtered

            frequencies, power = periodogram(
                filtered,
                fs=SAMPLE_RATE,
                scaling="spectrum"
            )

            # Only consider plausible pulse frequencies
            valid = (
                (frequencies >= 0.7) &
                (frequencies <= 3.5)
            )

            if not np.any(valid):
                return None

            valid_frequencies = frequencies[valid]
            valid_power = power[valid]

            dominant_frequency = valid_frequencies[
                np.argmax(valid_power)
            ]

            estimated_bpm = dominant_frequency * 60

            if 42 <= estimated_bpm <= 210:

                self.bpm = int(round(estimated_bpm))

                self.signal_quality = "Signal detected"

            else:

                self.signal_quality = "Unreliable signal"
                self.bpm = None

            return self.bpm

        except Exception as error:

            print("Signal processing error:", error)

            self.signal_quality = "Processing error"

            return None
class FaceAnalyzer:

    def __init__(self):

        self.age_net = None
        self.gender_net = None

        cascade_path = (
            Path(cv2.data.haarcascades) /
            "haarcascade_frontalface_default.xml"
        )

        self.face_detector = cv2.CascadeClassifier(
            str(cascade_path)
        )

        if self.face_detector.empty():
            raise RuntimeError("Could not load face detector.")

        required_files = [
            AGE_MODEL,
            AGE_CONFIG,
            GENDER_MODEL,
            GENDER_CONFIG
        ]

        missing = [
            str(path)
            for path in required_files
            if not path.exists()
        ]

        if missing:

            raise FileNotFoundError(
                "Missing model files:\n" + "\n".join(missing)
            )

        self.age_net = cv2.dnn.readNetFromCaffe(
            str(AGE_CONFIG),
            str(AGE_MODEL)
        )

        self.gender_net = cv2.dnn.readNetFromCaffe(
            str(GENDER_CONFIG),
            str(GENDER_MODEL)
        )

    def analyse(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        if len(faces) == 0:
            return None

        # Use the largest detected face
        x, y, w, h = max(
            faces,
            key=lambda face: face[2] * face[3]
        )

        face = frame[
            y:y + h,
            x:x + w
        ]

        if face.size == 0:
            return None

        blob = cv2.dnn.blobFromImage(
            face,
            scalefactor=1.0,
            size=(227, 227),
            mean=MODEL_MEAN_VALUES,
            swapRB=False
        )

        # Age prediction
        self.age_net.setInput(blob)

        age_predictions = self.age_net.forward()

        age_index = int(
            np.argmax(age_predictions[0])
        )

        age = AGE_LABELS[age_index]

        age_confidence = float(
            age_predictions[0][age_index]
        )

        # Gender prediction
        self.gender_net.setInput(blob)

        gender_predictions = self.gender_net.forward()

        gender_index = int(
            np.argmax(gender_predictions[0])
        )

        gender = GENDER_LABELS[gender_index]

        gender_confidence = float(
            gender_predictions[0][gender_index]
        )

        return {
            "box": (x, y, w, h),
            "age": age,
            "gender": gender,
            "age_confidence": age_confidence,
            "gender_confidence": gender_confidence
        }

class HeartBeatMonitorApp:

    def __init__(self, root):

        self.root = root

        self.root.title("HeartBeatMonitor")
        self.root.geometry("1250x780")
        self.root.minsize(1050, 700)

        self.root.configure(bg="#101827")

        self.running = True

        self.mode = "face"

        self.frame_count = 0

        self.age_group = None
        self.gender = None

        self.last_face_scan = 0

        self.face_result = None

        self.heartbeat = HeartbeatMonitor()

        self.face_analyzer = FaceAnalyzer()

        # Open camera
        self.camera = cv2.VideoCapture(CAMERA_INDEX)

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH, 640
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT, 480
        )

        self.camera.set(
            cv2.CAP_PROP_FPS, SAMPLE_RATE
        )

        if not self.camera.isOpened():

            raise RuntimeError(
                "Could not open camera. Check CAMERA_INDEX."
            )

        self.build_interface()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.end_program
        )

        self.update_camera()

    def build_interface(self):

        header = tk.Frame(
            self.root,
            bg="#172338",
            height=75
        )

        header.pack(fill="x")

        tk.Label(
            header,
            text="♥  HeartBeatMonitor",
            font=("Segoe UI", 23, "bold"),
            fg="#ffffff",
            bg="#172338"
        ).pack(side="left", padx=25, pady=15)

        self.mode_label = tk.Label(
            header,
            text="FACE ANALYSIS MODE",
            font=("Segoe UI", 11, "bold"),
            fg="#38bdf8",
            bg="#172338"
        )

        self.mode_label.pack(side="right", padx=25)

        main = tk.Frame(
            self.root,
            bg="#101827"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        # LEFT PANEL
        left = tk.Frame(
            main,
            bg="#172338",
            width=600
        )

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        left.pack_propagate(False)

        tk.Label(
            left,
            text="CAMERA FEED",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#172338"
        ).pack(anchor="w", padx=15, pady=12)

        self.video_label = tk.Label(
            left,
            bg="#080e18",
            text="Initialising camera...",
            fg="white"
        )

        self.video_label.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 12)
        )

        # RIGHT PANEL
        right = tk.Frame(
            main,
            bg="#172338",
            width=510
        )

        right.pack(
            side="right",
            fill="both",
            padx=(12, 0)
        )

        right.pack_propagate(False)

        tk.Label(
            right,
            text="HEART RATE",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#172338"
        ).pack(anchor="w", padx=18, pady=(15, 5))

        self.bpm_label = tk.Label(
            right,
            text="-- BPM",
            font=("Segoe UI", 34, "bold"),
            fg="#38bdf8",
            bg="#172338"
        )

        self.bpm_label.pack(pady=5)

        self.status_label = tk.Label(
            right,
            text="Waiting for measurement",
            font=("Segoe UI", 14, "bold"),
            fg="#94a3b8",
            bg="#172338"
        )

        self.status_label.pack(pady=5)

        self.quality_label = tk.Label(
            right,
            text="Waiting for finger...",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#172338"
        )

        self.quality_label.pack(pady=5)

        # GRAPH
        tk.Label(
            right,
            text="LIVE HEARTBEAT WAVEFORM",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#172338"
        ).pack(anchor="w", padx=18, pady=(15, 0))

        self.figure = Figure(
            figsize=(5, 2.3),
            dpi=100,
            facecolor="#172338"
        )

        self.axis = self.figure.add_subplot(111)

        self.axis.set_facecolor("#101827")

        self.axis.set_title(
            "Filtered pulse signal",
            color="white"
        )

        self.axis.set_xlabel(
            "Time (seconds)",
            color="white"
        )

        self.axis.tick_params(
            colors="white"
        )

        self.axis.spines["bottom"].set_color("#64748b")
        self.axis.spines["left"].set_color("#64748b")

        self.axis.grid(
            True,
            alpha=0.2
        )

        self.graph_line, = self.axis.plot(
            [],
            [],
            color="#22c55e",
            linewidth=1.5
        )

        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figure,
            master=right
        )

        self.canvas.get_tk_widget().pack(
            fill="x",
            padx=12,
            pady=8
        )

        # PERSONAL INFORMATION
        tk.Label(
            right,
            text="PERSON INFORMATION",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#172338"
        ).pack(anchor="w", padx=18, pady=(12, 5))

        self.age_label = tk.Label(
            right,
            text="Estimated age: Not scanned",
            font=("Segoe UI", 11),
            fg="#cbd5e1",
            bg="#172338"
        )

        self.age_label.pack(anchor="w", padx=20, pady=4)

        self.gender_label = tk.Label(
            right,
            text="Gender prediction: Not scanned",
            font=("Segoe UI", 11),
            fg="#cbd5e1",
            bg="#172338"
        )

        self.gender_label.pack(anchor="w", padx=20, pady=4)

        # BUTTONS
        buttons = tk.Frame(
            self.root,
            bg="#101827"
        )

        buttons.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        self.face_button = tk.Button(
            buttons,
            text="SCAN FACE",
            command=self.start_face_mode,
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2"
        )

        self.face_button.pack(
            side="left",
            padx=5
        )

        self.heart_button = tk.Button(
            buttons,
            text="START HEART MONITORING",
            command=self.start_heart_mode,
            font=("Segoe UI", 11, "bold"),
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2"
        )

        self.heart_button.pack(
            side="left",
            padx=5
        )

        self.end_button = tk.Button(
            buttons,
            text="END PROGRAM",
            command=self.end_program,
            font=("Segoe UI", 11, "bold"),
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            relief="flat",
            padx=20,
            pady=12,
            cursor="hand2"
        )

        self.end_button.pack(
            side="right",
            padx=5
        )

    def start_face_mode(self):

        self.mode = "face"

        self.mode_label.config(
            text="FACE ANALYSIS MODE",
            fg="#38bdf8"
        )

        self.face_result = None

        self.last_face_scan = 0

        self.video_label.config(
            text="Position your face in front of camera"
        )

    def scan_face(self, frame):

        current_time = time.monotonic()

        if current_time - self.last_face_scan < 1:
            return

        self.last_face_scan = current_time

        result = self.face_analyzer.analyse(frame)

        if result is None:
            return

        self.face_result = result

        self.age_group = result["age"]
        self.gender = result["gender"]

        self.age_label.config(
            text=f"Estimated age range: {self.age_group}"
        )

        self.gender_label.config(
            text=f"Gender prediction: {self.gender}"
        )

    def start_heart_mode(self):

        self.mode = "heart"

        self.heartbeat.reset()

        self.mode_label.config(
            text="FINGERTIP HEART MONITORING",
            fg="#22c55e"
        )

        self.bpm_label.config(
            text="-- BPM"
        )

        self.status_label.config(
            text="Collecting pulse signal",
            fg="#94a3b8"
        )

        self.quality_label.config(
            text="Place finger over camera lens"
        )

    def update_heart_display(self, bpm):

        self.quality_label.config(
            text=self.heartbeat.signal_quality
        )

        if bpm is None:

            self.bpm_label.config(
                text="-- BPM",
                fg="#38bdf8"
            )

            return

        status, colour = classify_heartbeat(
            bpm,
            self.age_group
        )

        self.bpm_label.config(
            text=f"{bpm} BPM",
            fg=colour
        )

        self.status_label.config(
            text=f"Heart rate: {status}",
            fg=colour
        )

    def update_graph(self):

        signal = self.heartbeat.filtered_signal

        if signal is None:
            return

        if len(signal) < 2:
            return

        signal = signal[-SAMPLE_RATE * 8:]

        x = np.linspace(
            -len(signal) / SAMPLE_RATE,
            0,
            len(signal)
        )

        # Normalise for graph display
        signal = signal - np.mean(signal)

        maximum = np.max(np.abs(signal))

        if maximum > 0:
            signal = signal / maximum

        self.graph_line.set_data(
            x,
            signal
        )

        self.axis.set_xlim(-8, 0)
        self.axis.set_ylim(-1.2, 1.2)

        self.canvas.draw_idle()

    def update_camera(self):

        if not self.running:
            return

        success, frame = self.camera.read()

        if success:

            self.frame_count += 1

            display_frame = frame.copy()

            if self.mode == "face":

                if self.frame_count % 10 == 0:

                    self.scan_face(frame)

                if self.face_result is not None:

                    x, y, w, h = self.face_result["box"]

                    cv2.rectangle(
                        display_frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2
                    )

                    label = (
                        f"{self.face_result['age']} "
                        f"| {self.face_result['gender']}"
                    )

                    cv2.putText(
                        display_frame,
                        label,
                        (x, max(y - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (0, 255, 0),
                        2
                    )

                cv2.putText(
                    display_frame,
                    "FACE ANALYSIS MODE",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2
                )

            elif self.mode == "heart":

                bpm = self.heartbeat.add_sample(frame)

                height, width = frame.shape[:2]

                x1 = int(width * 0.35)
                x2 = int(width * 0.65)

                y1 = int(height * 0.35)
                y2 = int(height * 0.65)

                cv2.rectangle(
                    display_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    display_frame,
                    "COVER CAMERA WITH FINGER",
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2
                )

                self.update_heart_display(bpm)

                self.update_graph()

            # Convert camera frame for Tkinter
            rgb_frame = cv2.cvtColor(
                display_frame,
                cv2.COLOR_BGR2RGB
            )

            image = Image.fromarray(rgb_frame)

            image = image.resize(
                (640, 480)
            )

            photo = ImageTk.PhotoImage(
                image=image
            )

            self.video_label.config(
                image=photo,
                text=""
            )

            self.video_label.image = photo

        self.root.after(
            33,
            self.update_camera
        )

    def end_program(self):

        if not self.running:
            return

        self.running = False

        if self.camera is not None:
            self.camera.release()

        cv2.destroyAllWindows()

        self.root.destroy()

if __name__ == "__main__":

    root = tk.Tk()

    try:

        application = HeartBeatMonitorApp(root)

        root.mainloop()

    except Exception as error:

        messagebox.showerror(
            "HeartBeatMonitor Error",
            str(error)
        )

        root.destroy()