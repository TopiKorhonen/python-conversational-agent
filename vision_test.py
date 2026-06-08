import os
import sys

os.environ["QT_QPA_PLATFORM"] = "xcb" #Wayland is cringe

import cv2
import time
from python_conversational_agent.vision import FacialAnalyzer

def main():
    print("Initializing...")
    try:

        analyzer = FacialAnalyzer(detector_backend="opencv")
        print("Model initialized successfully.")
    except Exception as e:
        print(f"Error initializing: {e}", file=sys.stderr)
        sys.exit(1)

    print("Opening webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.", file=sys.stderr)
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("\nStarting")
    print("Controls:")
    print("  - 'q' or 'ESC' to exit.")
    print("  - 'd' to cycle backends.")
    print("-" * 50)

    backends = ["opencv", "ssd", "mediapipe"]
    backend_idx = 0

    last_analysis_time = 0
    process_interval = 0.3
    faces = []

    fps_start_time = time.time()
    fps_counter = 0
    fps_text = "FPS: 0"

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.", file=sys.stderr)
            break

        current_time = time.time()

        frame = cv2.flip(frame, 1)

        if current_time - last_analysis_time >= process_interval:
            faces = analyzer.analyze_frame(frame)
            last_analysis_time = current_time

        fps_counter += 1
        if current_time - fps_start_time >= 1.0:
            fps_text = f"FPS: {fps_counter}"
            fps_counter = 0
            fps_start_time = current_time

        for face in faces:
            box = face["box"]
            x, y, w, h = box["x"], box["y"], box["w"], box["h"]

            color = (0, 255, 0) 
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            dominant = face["dominant_mapped_emotion"]
            conf = face["face_confidence"]
            label = f"{dominant.upper()} (conf: {conf:.2f})"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            mapped_emotions = face["mapped_emotions"]
            offset_y = y + h + 20
            for emotion_name, val in mapped_emotions.items():
                if val > 5.0:
                    text = f"{emotion_name}: {val:.1f}%"
                    cv2.putText(frame, text, (x, offset_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    offset_y += 18

        cv2.putText(frame, fps_text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Backend: {analyzer.detector_backend}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Test Program", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('d'):
            backend_idx = (backend_idx + 1) % len(backends)
            new_backend = backends[backend_idx]
            print(f"Switching detector backend to: {new_backend}")
            analyzer.detector_backend = new_backend

    cap.release()
    cv2.destroyAllWindows()
    print("Program exited successfully.")

if __name__ == "__main__":
    main()
