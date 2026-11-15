import cv2
import numpy as np
import time
import sys

# ==========================================
# CONFIGURATION
# ==========================================

CAMERA_INDEX = 0

WINDOW_NAME = "Astronaut Body Temperature Experiment"

# Terminate button coordinates
BUTTON_X1 = 20
BUTTON_Y1 = 300
BUTTON_X2 = 220
BUTTON_Y2 = 350

terminate_program = False

# ==========================================
# LOAD FACE DETECTOR
# ==========================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

if face_detector.empty():
    print("Error: Face detection model could not load.")
    sys.exit(1)

# ==========================================
# START CAMERA
# ==========================================

camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():
    print("Error: Cannot access laptop webcam.")
    sys.exit(1)

print("Webcam Skin Analysis Started")
print("Press Q or click TERMINATE PROGRAM to exit.")


# ==========================================
# MOUSE CLICK EVENT
# ==========================================

def mouse_callback(event, x, y, flags, param):

    global terminate_program

    if event == cv2.EVENT_LBUTTONDOWN:

        if (
            BUTTON_X1 <= x <= BUTTON_X2
            and BUTTON_Y1 <= y <= BUTTON_Y2
        ):

            terminate_program = True


cv2.namedWindow(WINDOW_NAME)

cv2.setMouseCallback(
    WINDOW_NAME,
    mouse_callback
)


# ==========================================
# MAIN CAMERA LOOP
# ==========================================

try:

    while True:

        if terminate_program:
            break

        ret, frame = camera.read()

        if not ret:
            print("Unable to read webcam.")
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)

        # Convert to grayscale
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        # ==================================
        # DASHBOARD HEADER
        # ==================================

        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], 65),
            (25, 35, 55),
            -1
        )

        cv2.putText(
            frame,
            "ASTRONAUT HEALTH MONITORING",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # ==================================
        # FACE DETECTION
        # ==================================

        if len(faces) == 0:

            cv2.putText(
                frame,
                "No face detected - Position yourself in camera",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 165, 255),
                2
            )

        for (x, y, w, h) in faces:

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            # Cheek regions
            left_cheek = frame[
                y + int(h * 0.50): y + int(h * 0.75),
                x + int(w * 0.15): x + int(w * 0.40)
            ]

            right_cheek = frame[
                y + int(h * 0.50): y + int(h * 0.75),
                x + int(w * 0.60): x + int(w * 0.85)
            ]

            cheek_regions = [
                left_cheek,
                right_cheek
            ]

            valid_regions = [
                region for region in cheek_regions
                if region.size > 0
            ]

            if not valid_regions:
                continue

            average_colours = [
                np.mean(region, axis=(0, 1))
                for region in valid_regions
            ]

            average_bgr = np.mean(
                average_colours,
                axis=0
            )

            blue, green, red = average_bgr

            # Highlight cheek regions
            cv2.rectangle(
                frame,
                (x + int(w * 0.15), y + int(h * 0.50)),
                (x + int(w * 0.40), y + int(h * 0.75)),
                (255, 255, 0),
                2
            )

            cv2.rectangle(
                frame,
                (x + int(w * 0.60), y + int(h * 0.50)),
                (x + int(w * 0.85), y + int(h * 0.75)),
                (255, 255, 0),
                2
            )

            # RGB information
            cv2.putText(
                frame,
                f"Red: {red:.1f}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                f"Green: {green:.1f}",
                (20, 145),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Blue: {blue:.1f}",
                (20, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 100, 0),
                2
            )

            cv2.putText(
                frame,
                "Body Temperature: NOT AVAILABLE",
                (20, 225),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 165, 255),
                2
            )

            cv2.putText(
                frame,
                "RGB analysis only - No thermal measurement",
                (20, 260),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1
            )

        # ==================================
        # TERMINATE PROGRAM BUTTON
        # ==================================

        cv2.rectangle(
            frame,
            (BUTTON_X1, BUTTON_Y1),
            (BUTTON_X2, BUTTON_Y2),
            (0, 0, 200),
            -1
        )

        cv2.rectangle(
            frame,
            (BUTTON_X1, BUTTON_Y1),
            (BUTTON_X2, BUTTON_Y2),
            (255, 255, 255),
            2
        )

        button_text = "TERMINATE PROGRAM"

        text_size = cv2.getTextSize(
            button_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            2
        )[0]

        text_x = BUTTON_X1 + (
            (BUTTON_X2 - BUTTON_X1 - text_size[0]) // 2
        )

        text_y = BUTTON_Y1 + (
            (BUTTON_Y2 - BUTTON_Y1 + text_size[1]) // 2
        )

        cv2.putText(
            frame,
            button_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2
        )

        # ==================================
        # DISPLAY WINDOW
        # ==================================

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

        # Exit using Q or ESC
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break

finally:

    # ======================================
    # CLEANUP
    # ======================================

    camera.release()

    cv2.destroyAllWindows()

    print("Monitoring stopped.")
    print("Camera released successfully.")
